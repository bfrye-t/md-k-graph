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
    ) -> List[dict]:
        """
        Traverse the graph from given nodes to find related entities.

        Args:
            node_ids: List of node IDs to start from.
            hops: Number of relationship hops to traverse (1 or 2).

        Returns:
            List of dictionaries containing paths and related nodes.
        """
        if hops == 1:
            query = """
            MATCH (start:__Entity__)
            WHERE start.id IN $node_ids
            OPTIONAL MATCH (start)-[r]-(neighbor:__Entity__)
            RETURN start.id AS source,
                   type(r) AS relationship,
                   neighbor.id AS target,
                   neighbor.description AS target_description,
                   labels(neighbor) AS target_labels
            """
        else:  # 2-hop
            query = """
            MATCH (start:__Entity__)
            WHERE start.id IN $node_ids
            OPTIONAL MATCH path = (start)-[*1..2]-(neighbor:__Entity__)
            WHERE start <> neighbor
            WITH start, neighbor, relationships(path) AS rels
            RETURN DISTINCT
                   start.id AS source,
                   [r IN rels | type(r)] AS relationships,
                   neighbor.id AS target,
                   neighbor.description AS target_description,
                   labels(neighbor) AS target_labels
            LIMIT 50
            """

        results = self.graph.query(query, {"node_ids": node_ids})
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
