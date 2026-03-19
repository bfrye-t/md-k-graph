"""
Step 2: Graph Extraction

Uses LangChain's LLMGraphTransformer with a strictly enforced ontology
to extract knowledge graph nodes and relationships from document chunks.
"""

from typing import List, Optional

from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.graphs.graph_document import GraphDocument

import config


def get_llm():
    """Get the configured LLM instance."""
    if config.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.LLM_MODEL,
            temperature=0,  # Deterministic for consistent extraction
        )
    elif config.LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.LLM_MODEL,
            temperature=0,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")


def create_graph_transformer() -> LLMGraphTransformer:
    """
    Create an LLMGraphTransformer with strictly enforced schema.

    The allowed_nodes and allowed_relationships parameters constrain
    the LLM to only extract entities and relationships from our ontology.
    """
    llm = get_llm()

    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=config.ALLOWED_NODES,
        allowed_relationships=config.ALLOWED_RELATIONSHIPS,
        node_properties=["description"],  # Extract descriptions for nodes
        relationship_properties=["description"],  # And for relationships
        strict_mode=True,  # Enforce the schema strictly
    )

    return transformer


def extract_graph_from_documents(
    documents: List[Document],
    batch_size: int = 5,
    verbose: bool = True,
) -> List[GraphDocument]:
    """
    Extract knowledge graph from document chunks.

    Args:
        documents: List of chunked Document objects.
        batch_size: Number of documents to process in each batch.
        verbose: Whether to print progress.

    Returns:
        List of GraphDocument objects containing nodes and relationships.
    """
    import time

    transformer = create_graph_transformer()
    all_graph_docs = []

    total = len(documents)
    total_batches = (total + batch_size - 1) // batch_size

    if verbose:
        print(f"    Starting extraction: {total} chunks in {total_batches} batches", flush=True)

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        if verbose:
            print(f"    📦 Batch {batch_num}/{total_batches} ({len(batch)} chunks)...", end=" ", flush=True)

        batch_start = time.time()
        try:
            # Convert documents to graph documents
            graph_docs = transformer.convert_to_graph_documents(batch)
            all_graph_docs.extend(graph_docs)

            batch_time = time.time() - batch_start

            if verbose:
                # Count extracted elements
                nodes = sum(len(gd.nodes) for gd in graph_docs)
                rels = sum(len(gd.relationships) for gd in graph_docs)
                print(f"✓ {nodes} nodes, {rels} rels ({batch_time:.1f}s)", flush=True)

        except Exception as e:
            print(f"✗ Error: {e}", flush=True)
            continue

    # Summary statistics
    if verbose:
        total_nodes = sum(len(gd.nodes) for gd in all_graph_docs)
        total_rels = sum(len(gd.relationships) for gd in all_graph_docs)
        print(f"\n    === Extraction Complete ===", flush=True)
        print(f"    Total nodes: {total_nodes}", flush=True)
        print(f"    Total relationships: {total_rels}", flush=True)
        print(f"    Graph documents: {len(all_graph_docs)}", flush=True)

    return all_graph_docs


def summarize_graph_documents(graph_docs: List[GraphDocument]) -> dict:
    """
    Generate summary statistics about extracted graph.

    Returns:
        Dictionary with node type counts, relationship type counts, etc.
    """
    node_types = {}
    rel_types = {}

    for gd in graph_docs:
        for node in gd.nodes:
            node_type = node.type
            node_types[node_type] = node_types.get(node_type, 0) + 1

        for rel in gd.relationships:
            rel_type = rel.type
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1

    return {
        "node_type_counts": node_types,
        "relationship_type_counts": rel_types,
        "total_nodes": sum(node_types.values()),
        "total_relationships": sum(rel_types.values()),
    }


def print_sample_extractions(graph_docs: List[GraphDocument], max_samples: int = 10):
    """Print sample nodes and relationships for inspection."""
    print("\n--- Sample Nodes ---")
    node_count = 0
    for gd in graph_docs:
        for node in gd.nodes:
            if node_count >= max_samples:
                break
            print(f"  [{node.type}] {node.id}")
            if hasattr(node, 'properties') and node.properties:
                desc = node.properties.get('description', '')[:80]
                if desc:
                    print(f"      {desc}...")
            node_count += 1
        if node_count >= max_samples:
            break

    print("\n--- Sample Relationships ---")
    rel_count = 0
    for gd in graph_docs:
        for rel in gd.relationships:
            if rel_count >= max_samples:
                break
            print(f"  ({rel.source.id}) -[{rel.type}]-> ({rel.target.id})")
            rel_count += 1
        if rel_count >= max_samples:
            break


if __name__ == "__main__":
    # Test extraction on a small sample
    from ingestion import load_markdown_files, chunk_documents

    docs = load_markdown_files()
    chunks = chunk_documents(docs)

    # Just test on first 3 chunks
    test_chunks = chunks[:3]
    print(f"\nTesting extraction on {len(test_chunks)} chunks...")

    graph_docs = extract_graph_from_documents(test_chunks, batch_size=3)

    summary = summarize_graph_documents(graph_docs)
    print(f"\nNode types: {summary['node_type_counts']}")
    print(f"Relationship types: {summary['relationship_type_counts']}")

    print_sample_extractions(graph_docs)
