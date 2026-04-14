"""
Step 3: Storage & Indexing in Neo4j

Handles Neo4j connection, graph document loading, and vector index creation
for hybrid semantic + graph retrieval.
"""

from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument
from langchain_neo4j import Neo4jGraph, Neo4jVector

import config


class GraphStorage:
    """
    Manages Neo4j graph storage and vector indexing.
    """

    def __init__(
        self,
        uri: str = None,
        username: str = None,
        password: str = None,
        database: str = None,
    ):
        """
        Initialize connection to Neo4j.

        Args:
            uri: Neo4j connection URI. Defaults to config.NEO4J_URI.
            username: Neo4j username. Defaults to config.NEO4J_USERNAME.
            password: Neo4j password. Defaults to config.NEO4J_PASSWORD.
            database: Neo4j database name. Defaults to config.NEO4J_DATABASE.
        """
        self.uri = uri or config.NEO4J_URI
        self.username = username or config.NEO4J_USERNAME
        self.password = password or config.NEO4J_PASSWORD
        self.database = database or config.NEO4J_DATABASE

        if not all([self.uri, self.username, self.password]):
            raise ValueError(
                "Neo4j credentials not found. "
                "Set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD in .env file."
            )

        # Initialize the graph connection
        self.graph = Neo4jGraph(
            url=self.uri,
            username=self.username,
            password=self.password,
            database=self.database,
        )

        self._vector_store = None

    def clear_database(self, confirm: bool = False):
        """
        Clear all nodes and relationships from the database.

        Args:
            confirm: Must be True to actually clear the database.
        """
        if not confirm:
            print("Database clear aborted. Pass confirm=True to proceed.")
            return

        print("Clearing database...")
        self.graph.query("MATCH (n) DETACH DELETE n")
        print("Database cleared.")

    def load_graph_documents(
        self,
        graph_documents: List[GraphDocument],
        include_source: bool = True,
    ):
        """
        Load extracted graph documents into Neo4j.

        Args:
            graph_documents: List of GraphDocument objects from extraction.
            include_source: Whether to create Document nodes linked to entities.
        """
        print(f"Loading {len(graph_documents)} graph documents into Neo4j...")

        # Use Neo4jGraph's built-in method to add graph documents
        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,  # Add __Entity__ label to all nodes
            include_source=include_source,  # Link entities to source Document
        )

        # Refresh the schema
        self.graph.refresh_schema()

        print("Graph documents loaded successfully.")
        print(f"Schema: {self.graph.schema}")

    def load_document_chunks(self, chunks: List[Document]):
        """
        Load document chunks as Document nodes for vector search.

        These nodes store the chunk text and metadata, enabling
        semantic search over the original content.
        """
        total = len(chunks)

        for i, chunk in enumerate(chunks):
            # Create Document node with text and metadata
            query = """
            MERGE (d:Document {chunk_id: $chunk_id})
            SET d.text = $text,
                d.doc_title = $doc_title,
                d.doc_order = $doc_order,
                d.h1_header = $h1_header,
                d.h2_header = $h2_header,
                d.h3_header = $h3_header,
                d.source = $source
            """
            params = {
                "chunk_id": chunk.metadata.get("chunk_id", ""),
                "text": chunk.page_content,
                "doc_title": chunk.metadata.get("doc_title", ""),
                "doc_order": chunk.metadata.get("doc_order", 0),
                "h1_header": chunk.metadata.get("h1_header", ""),
                "h2_header": chunk.metadata.get("h2_header", ""),
                "h3_header": chunk.metadata.get("h3_header", ""),
                "source": chunk.metadata.get("source", ""),
            }
            self.graph.query(query, params)

            # Progress update every 10 chunks
            if (i + 1) % 10 == 0 or i == total - 1:
                print(f"    Loaded {i + 1}/{total} chunks...", flush=True)

    def create_vector_index(self) -> Neo4jVector:
        """
        Create vector embeddings for Document nodes.

        Uses Neo4jVector.from_existing_graph to embed the 'text' property
        of Document nodes, enabling semantic similarity search.

        Returns:
            Neo4jVector instance for querying.
        """
        print("Creating vector index on Document nodes...")

        # Get embeddings model
        if config.LLM_PROVIDER == "openai":
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
        else:
            # Fallback to OpenAI embeddings even with Anthropic LLM
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

        # Create vector index from existing Document nodes
        self._vector_store = Neo4jVector.from_existing_graph(
            embedding=embeddings,
            url=self.uri,
            username=self.username,
            password=self.password,
            database=self.database,
            index_name=config.VECTOR_INDEX_NAME,
            node_label="Document",
            text_node_properties=["text"],  # Embed the text property
            embedding_node_property="embedding",  # Store embedding here
        )

        print(f"Vector index '{config.VECTOR_INDEX_NAME}' created.")
        return self._vector_store

    def get_vector_store(self) -> Neo4jVector:
        """Get or create the vector store."""
        if self._vector_store is None:
            self._vector_store = self.create_vector_index()
        return self._vector_store

    def get_existing_vector_store(self) -> Optional[Neo4jVector]:
        """
        Connect to an existing vector index without regenerating embeddings.

        Returns:
            Neo4jVector instance if index exists, None otherwise.
        """
        if config.LLM_PROVIDER == "openai":
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)
        else:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

        try:
            self._vector_store = Neo4jVector.from_existing_index(
                embedding=embeddings,
                url=self.uri,
                username=self.username,
                password=self.password,
                database=self.database,
                index_name=config.VECTOR_INDEX_NAME,
            )
            return self._vector_store
        except Exception as e:
            print(f"Note: Could not connect to existing index: {e}")
            return None

    def add_embeddings_incrementally(self, chunks: List[Document]) -> int:
        """
        Add embeddings for new document chunks without regenerating all.

        Uses Neo4jVector.add_texts() to add only the new chunks to the
        existing vector index.

        Args:
            chunks: List of Document objects to embed and add.

        Returns:
            Number of chunks added.
        """
        if not chunks:
            return 0

        # Ensure we have a vector store
        vector_store = self.get_existing_vector_store()
        if vector_store is None:
            print("No existing index found, creating new one...")
            vector_store = self.create_vector_index()
            return len(chunks)  # All chunks were added via from_existing_graph

        # Add texts incrementally
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.metadata.get("chunk_id") for chunk in chunks]

        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )

        print(f"Added {len(chunks)} embeddings incrementally.")
        return len(chunks)

    def create_fulltext_index(self):
        """Create fulltext index for keyword search on entity nodes."""
        print("Creating fulltext index on entity nodes...")

        # Create fulltext index on __Entity__ nodes
        query = """
        CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
        FOR (n:__Entity__)
        ON EACH [n.id, n.description]
        """
        try:
            self.graph.query(query)
            print("Fulltext index created.")
        except Exception as e:
            print(f"Fulltext index may already exist: {e}")

    def vector_search(self, query: str, k: int = 5) -> List[Document]:
        """
        Perform semantic search on Document nodes.

        Args:
            query: Search query string.
            k: Number of results to return.

        Returns:
            List of Document objects with similarity scores.
        """
        vector_store = self.get_vector_store()
        results = vector_store.similarity_search_with_score(query, k=k)

        # Convert to list of documents with scores in metadata
        docs = []
        for doc, score in results:
            doc.metadata["similarity_score"] = score
            docs.append(doc)

        return docs

    def graph_traverse(
        self,
        node_ids: List[str],
        hops: int = 1,
        limit: int = 25,
        filter_relationship_types: bool = True,
        direction: str = "bidirectional",
    ) -> List[dict]:
        """
        Traverse the graph from given nodes to find related entities.

        Args:
            node_ids: List of node IDs to start from.
            hops: Number of relationship hops to traverse (1 or 2).
            limit: Maximum number of results to return.
            filter_relationship_types: If True, only return schema-defined relationships.
            direction: "bidirectional", "outgoing_only", or "incoming_only".

        Returns:
            List of dictionaries containing paths and related nodes.
        """
        # Build relationship type filter clause
        rel_type_filter = ""
        if filter_relationship_types:
            allowed_types = "', '".join(config.ALLOWED_RELATIONSHIPS)
            rel_type_filter = f"AND type(r) IN ['{allowed_types}']"

        if hops == 1:
            # Build relationship pattern based on direction
            if direction == "outgoing_only":
                rel_pattern = "(start)-[r]->(neighbor:__Entity__)"
            elif direction == "incoming_only":
                rel_pattern = "(start)<-[r]-(neighbor:__Entity__)"
            else:  # bidirectional
                rel_pattern = "(start)-[r]-(neighbor:__Entity__)"

            query = f"""
            MATCH (start:__Entity__)
            WHERE start.id IN $node_ids
            OPTIONAL MATCH {rel_pattern}
            WHERE neighbor IS NULL OR (neighbor <> start {rel_type_filter})
            RETURN start.id AS source,
                   type(r) AS relationship,
                   neighbor.id AS target,
                   neighbor.description AS target_description,
                   labels(neighbor) AS target_labels
            LIMIT $limit
            """
        else:  # 2-hop
            # Build path pattern based on direction
            if direction == "outgoing_only":
                path_pattern = "(start)-[*1..2]->(neighbor:__Entity__)"
            elif direction == "incoming_only":
                path_pattern = "(start)<-[*1..2]-(neighbor:__Entity__)"
            else:  # bidirectional
                path_pattern = "(start)-[*1..2]-(neighbor:__Entity__)"

            # For 2-hop, filter each relationship in the path
            path_rel_filter = ""
            if filter_relationship_types:
                allowed_types = "', '".join(config.ALLOWED_RELATIONSHIPS)
                path_rel_filter = f"AND ALL(r IN rels WHERE type(r) IN ['{allowed_types}'])"

            query = f"""
            MATCH (start:__Entity__)
            WHERE start.id IN $node_ids
            OPTIONAL MATCH path = {path_pattern}
            WHERE start <> neighbor
            WITH start, neighbor, relationships(path) AS rels
            WHERE rels IS NULL OR (size(rels) > 0 {path_rel_filter})
            RETURN DISTINCT
                   start.id AS source,
                   [r IN rels | type(r)] AS relationships,
                   neighbor.id AS target,
                   neighbor.description AS target_description,
                   labels(neighbor) AS target_labels
            LIMIT $limit
            """

        results = self.graph.query(query, {"node_ids": node_ids, "limit": limit})
        return results

    def get_entity_by_text(self, text: str, limit: int = 5) -> List[dict]:
        """
        Find entities that match the given text (fuzzy match).

        Args:
            text: Text to search for in entity IDs.
            limit: Maximum number of results.

        Returns:
            List of matching entity dictionaries.
        """
        query = """
        MATCH (n:__Entity__)
        WHERE toLower(n.id) CONTAINS toLower($text)
           OR toLower(n.description) CONTAINS toLower($text)
        RETURN n.id AS id,
               labels(n) AS labels,
               n.description AS description
        LIMIT $limit
        """
        return self.graph.query(query, {"text": text, "limit": limit})

    def resolve_entities(self, entity_names: List[str]) -> List[dict]:
        """
        Resolve entity names to actual graph nodes with confidence scores.

        Uses a multi-strategy matching approach:
        1. Exact match on n.id (confidence: 1.0)
        2. Normalized match - case-insensitive, trimmed (confidence: 0.9)
        3. Fuzzy CONTAINS match (confidence: 0.5-0.7)

        Args:
            entity_names: List of entity names to resolve.

        Returns:
            List of matched entities with confidence scores, sorted by confidence.
            Each entry has: id, labels, description, confidence, match_type
        """
        if not entity_names:
            return []

        results = []

        for name in entity_names:
            name_clean = name.strip()
            name_lower = name_clean.lower()

            # Strategy 1: Exact match
            exact_query = """
            MATCH (n:__Entity__)
            WHERE n.id = $name
            RETURN n.id AS id,
                   labels(n) AS labels,
                   n.description AS description,
                   'exact' AS match_type
            LIMIT 1
            """
            exact_results = self.graph.query(exact_query, {"name": name_clean})
            if exact_results:
                for r in exact_results:
                    r["confidence"] = 1.0
                    results.append(r)
                continue  # Found exact match, skip other strategies

            # Strategy 2: Normalized match (case-insensitive)
            normalized_query = """
            MATCH (n:__Entity__)
            WHERE toLower(trim(n.id)) = toLower(trim($name))
            RETURN n.id AS id,
                   labels(n) AS labels,
                   n.description AS description,
                   'normalized' AS match_type
            LIMIT 1
            """
            norm_results = self.graph.query(normalized_query, {"name": name_clean})
            if norm_results:
                for r in norm_results:
                    r["confidence"] = 0.9
                    results.append(r)
                continue  # Found normalized match, skip fuzzy

            # Strategy 3: Fuzzy CONTAINS match
            fuzzy_query = """
            MATCH (n:__Entity__)
            WHERE toLower(n.id) CONTAINS toLower($name)
               OR toLower($name) CONTAINS toLower(n.id)
            RETURN n.id AS id,
                   labels(n) AS labels,
                   n.description AS description,
                   'fuzzy' AS match_type
            LIMIT 3
            """
            fuzzy_results = self.graph.query(fuzzy_query, {"name": name_clean})
            for r in fuzzy_results:
                # Calculate confidence based on length ratio
                match_id_lower = r["id"].lower()
                if name_lower in match_id_lower:
                    # Query is substring of entity ID
                    ratio = len(name_lower) / len(match_id_lower)
                    r["confidence"] = 0.5 + (0.2 * ratio)
                elif match_id_lower in name_lower:
                    # Entity ID is substring of query
                    ratio = len(match_id_lower) / len(name_lower)
                    r["confidence"] = 0.5 + (0.2 * ratio)
                else:
                    r["confidence"] = 0.5
                results.append(r)

        # Sort by confidence descending and deduplicate by id
        seen_ids = set()
        unique_results = []
        for r in sorted(results, key=lambda x: x["confidence"], reverse=True):
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                unique_results.append(r)

        return unique_results

    def remove_document_chunks(self, chunk_ids: List[str]) -> int:
        """
        Remove document chunks by their IDs.

        Used during incremental updates to clean up chunks from
        modified or deleted files before re-processing.

        Args:
            chunk_ids: List of chunk IDs to remove.

        Returns:
            Number of nodes deleted.
        """
        if not chunk_ids:
            return 0

        query = """
        MATCH (d:Document)
        WHERE d.chunk_id IN $chunk_ids
        DETACH DELETE d
        RETURN count(d) AS deleted_count
        """
        result = self.graph.query(query, {"chunk_ids": chunk_ids})
        deleted = result[0]["deleted_count"] if result else 0
        print(f"Removed {deleted} document chunks.")
        return deleted

    def remove_entities_by_ids(self, entity_ids: List[str]) -> int:
        """
        Remove entity nodes by their IDs.

        Used to clean up entities that were extracted from files
        that have been deleted or modified.

        Args:
            entity_ids: List of entity IDs to remove.

        Returns:
            Number of nodes deleted.
        """
        if not entity_ids:
            return 0

        query = """
        MATCH (n:__Entity__)
        WHERE n.id IN $entity_ids
        DETACH DELETE n
        RETURN count(n) AS deleted_count
        """
        result = self.graph.query(query, {"entity_ids": entity_ids})
        deleted = result[0]["deleted_count"] if result else 0
        print(f"Removed {deleted} entity nodes.")
        return deleted

    def get_orphaned_entities(self) -> List[str]:
        """
        Find entity nodes that have no relationships.

        These are candidates for cleanup after document deletion.

        Returns:
            List of orphaned entity IDs.
        """
        query = """
        MATCH (n:__Entity__)
        WHERE NOT (n)-[]-()
        RETURN n.id AS id
        """
        results = self.graph.query(query)
        return [r["id"] for r in results if r["id"]]

    def cleanup_orphaned_entities(self) -> int:
        """
        Remove all entity nodes that have no relationships.

        Returns:
            Number of orphaned entities removed.
        """
        query = """
        MATCH (n:__Entity__)
        WHERE NOT (n)-[]-()
        DELETE n
        RETURN count(n) AS deleted_count
        """
        result = self.graph.query(query)
        deleted = result[0]["deleted_count"] if result else 0
        if deleted > 0:
            print(f"Cleaned up {deleted} orphaned entities.")
        return deleted

    def get_schema_summary(self) -> str:
        """Get a summary of the graph schema."""
        return self.graph.schema

    def get_statistics(self) -> dict:
        """Get database statistics."""
        node_count = self.graph.query("MATCH (n) RETURN count(n) AS count")[0]["count"]
        rel_count = self.graph.query("MATCH ()-[r]->() RETURN count(r) AS count")[0]["count"]

        # Node type counts
        node_types = self.graph.query("""
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(*) AS count
            ORDER BY count DESC
        """)

        # Relationship type counts
        rel_types = self.graph.query("""
            MATCH ()-[r]->()
            RETURN type(r) AS type, count(*) AS count
            ORDER BY count DESC
        """)

        return {
            "total_nodes": node_count,
            "total_relationships": rel_count,
            "node_types": {r["label"]: r["count"] for r in node_types},
            "relationship_types": {r["type"]: r["count"] for r in rel_types},
        }


if __name__ == "__main__":
    # Test connection
    storage = GraphStorage()
    print("Connected to Neo4j successfully!")
    print(f"Current schema: {storage.get_schema_summary()}")

    stats = storage.get_statistics()
    print(f"Statistics: {stats}")
