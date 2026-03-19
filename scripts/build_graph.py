#!/usr/bin/env python3
"""
Build Graph Script

One-time script to:
1. Load and chunk markdown documents
2. Extract knowledge graph using LLM
3. Load graph into Neo4j
4. Create vector embeddings

Usage:
    python scripts/build_graph.py [--clear] [--skip-extraction]

Options:
    --clear            Clear existing database before loading
    --skip-extraction  Skip LLM extraction (just load chunks for vector search)
"""

import sys
import argparse
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import load_markdown_files, chunk_documents, get_chunk_summary
from src.graph_extraction import (
    extract_graph_from_documents,
    summarize_graph_documents,
    print_sample_extractions,
)
from src.graph_storage import GraphStorage


def log(msg: str):
    """Print with flush for real-time output."""
    print(msg, flush=True)


def log_step(step_num: int, total: int, msg: str):
    """Print a step with progress indicator."""
    print(f"\n[Step {step_num}/{total}] {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Build the knowledge graph from markdown files")
    parser.add_argument("--clear", action="store_true", help="Clear database before loading")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip LLM graph extraction")
    parser.add_argument("--batch-size", type=int, default=3, help="Batch size for LLM extraction")
    args = parser.parse_args()

    total_steps = 8 if not args.skip_extraction else 6
    start_time = time.time()

    log("=" * 60)
    log("GraphRAG Knowledge Graph Builder")
    log("=" * 60)

    # Step 1: Load and chunk documents
    log_step(1, total_steps, "Loading markdown files...")
    documents = load_markdown_files()
    log(f"  ✓ Loaded {len(documents)} files")

    # Step 2: Chunk documents
    log_step(2, total_steps, "Chunking documents by headers...")
    chunks = chunk_documents(documents)
    log(f"  ✓ Created {len(chunks)} chunks")

    # Show sample chunks
    log("\n  Sample chunks:")
    for chunk in chunks[:3]:
        log(f"    {get_chunk_summary(chunk)}")

    # Step 3: Connect to Neo4j
    log_step(3, total_steps, "Connecting to Neo4j...")
    storage = GraphStorage()
    log("  ✓ Connected successfully!")

    # Clear if requested
    if args.clear:
        confirm = input("\n  ⚠️  This will DELETE all data in the database. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            storage.clear_database(confirm=True)
            log("  ✓ Database cleared")
        else:
            log("  ✗ Clear aborted.")

    current_step = 4

    # Step 4: Extract knowledge graph (unless skipped)
    if not args.skip_extraction:
        log_step(current_step, total_steps, f"Extracting knowledge graph via LLM (batch_size={args.batch_size})...")
        log("  ⏳ This may take several minutes depending on document size...")
        log(f"  Processing {len(chunks)} chunks...")

        extraction_start = time.time()
        graph_docs = extract_graph_from_documents(
            chunks,
            batch_size=args.batch_size,
            verbose=True,
        )
        extraction_time = time.time() - extraction_start

        # Print summary
        summary = summarize_graph_documents(graph_docs)
        log(f"\n  ✓ Extraction complete in {extraction_time:.1f}s")
        log(f"    Node types: {summary['node_type_counts']}")
        log(f"    Relationship types: {summary['relationship_type_counts']}")

        # Print samples
        print_sample_extractions(graph_docs, max_samples=5)

        # Step 5: Load graph documents
        current_step += 1
        log_step(current_step, total_steps, "Loading graph documents into Neo4j...")
        load_start = time.time()
        storage.load_graph_documents(graph_docs, include_source=True)
        log(f"  ✓ Loaded in {time.time() - load_start:.1f}s")

        current_step += 1
    else:
        log_step(current_step, total_steps, "Skipping graph extraction (--skip-extraction flag)")
        current_step += 1

    # Step 6: Load document chunks (for vector search)
    log_step(current_step, total_steps, "Loading document chunks for vector search...")
    chunk_start = time.time()
    for i, chunk in enumerate(chunks):
        if (i + 1) % 10 == 0 or i == len(chunks) - 1:
            log(f"    Loading chunk {i + 1}/{len(chunks)}...")
    storage.load_document_chunks(chunks)
    log(f"  ✓ Loaded {len(chunks)} chunks in {time.time() - chunk_start:.1f}s")

    current_step += 1

    # Step 7: Create vector index
    log_step(current_step, total_steps, "Creating vector embeddings & index...")
    log("  ⏳ Generating embeddings for all document chunks...")
    vector_start = time.time()
    storage.create_vector_index()
    log(f"  ✓ Vector index created in {time.time() - vector_start:.1f}s")

    current_step += 1

    # Step 8: Create fulltext index
    log_step(current_step, total_steps, "Creating fulltext index...")
    storage.create_fulltext_index()
    log("  ✓ Fulltext index created")

    # Final statistics
    total_time = time.time() - start_time
    log("\n" + "=" * 60)
    log(f"Build Complete! (Total time: {total_time:.1f}s)")
    log("=" * 60)

    stats = storage.get_statistics()
    log(f"\nDatabase Statistics:")
    log(f"  Total nodes: {stats['total_nodes']}")
    log(f"  Total relationships: {stats['total_relationships']}")
    log(f"\n  Node types:")
    for label, count in sorted(stats['node_types'].items(), key=lambda x: -x[1]):
        log(f"    {label}: {count}")
    log(f"\n  Relationship types:")
    for rel_type, count in sorted(stats['relationship_types'].items(), key=lambda x: -x[1]):
        log(f"    {rel_type}: {count}")

    log("\n✓ Knowledge graph is ready for querying!")
    log("  Run: streamlit run app.py")


if __name__ == "__main__":
    main()
