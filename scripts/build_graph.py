#!/usr/bin/env python3
"""
Build Graph Script

Builds or incrementally updates the knowledge graph from markdown files.

Usage:
    python scripts/build_graph.py              # Incremental update (default)
    python scripts/build_graph.py --full       # Force full rebuild
    python scripts/build_graph.py --dry-run    # Show what would change
    python scripts/build_graph.py --clear      # Clear DB and rebuild

Options:
    --clear            Clear existing database before loading
    --full             Force full rebuild (ignore manifest)
    --dry-run          Show what would change without making changes
    --skip-extraction  Skip LLM extraction (just load chunks for vector search)
    --batch-size N     Batch size for LLM extraction (default: 3)
"""

import sys
import argparse
import time
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import load_markdown_files, load_specific_files, chunk_documents, get_chunk_summary
from src.graph_extraction import (
    extract_graph_from_documents,
    summarize_graph_documents,
    print_sample_extractions,
)
from src.graph_storage import GraphStorage
from src.manifest import ManifestManager, ChangeSet, compute_file_hash

import config


def log(msg: str):
    """Print with flush for real-time output."""
    print(msg, flush=True)


def log_step(step_num: int, total: int, msg: str):
    """Print a step with progress indicator."""
    print(f"\n[Step {step_num}/{total}] {msg}", flush=True)


def get_entity_ids_from_graph_docs(graph_docs) -> List[str]:
    """Extract entity IDs from graph documents."""
    entity_ids = set()
    for gd in graph_docs:
        for node in gd.nodes:
            if node.id:
                entity_ids.add(node.id)
    return list(entity_ids)


def process_files(
    filenames: List[str],
    storage: GraphStorage,
    manifest: ManifestManager,
    args,
    is_incremental: bool = False,
) -> dict:
    """
    Process a set of files: load, chunk, extract, and store.

    Args:
        filenames: List of filenames to process
        storage: GraphStorage instance
        manifest: ManifestManager instance
        args: Command-line arguments
        is_incremental: Whether this is an incremental update

    Returns:
        Dict with processing results
    """
    results = {
        "files_processed": 0,
        "chunks_created": 0,
        "entities_extracted": 0,
    }

    if not filenames:
        return results

    # Load documents
    log(f"  Loading {len(filenames)} file(s)...")
    documents = load_specific_files(filenames)
    results["files_processed"] = len(documents)

    # Chunk documents with stable IDs
    log("  Chunking documents...")
    chunks = chunk_documents(documents, use_stable_ids=True)
    results["chunks_created"] = len(chunks)

    # Group chunks by source file for manifest tracking
    chunks_by_file = {}
    for chunk in chunks:
        filename = chunk.metadata.get("filename", "unknown")
        if filename not in chunks_by_file:
            chunks_by_file[filename] = []
        chunks_by_file[filename].append(chunk)

    # Extract knowledge graph (unless skipped)
    graph_docs = []
    entity_ids_by_file = {}

    if not args.skip_extraction:
        log(f"  Extracting knowledge graph via LLM (batch_size={args.batch_size})...")
        extraction_start = time.time()

        graph_docs = extract_graph_from_documents(
            chunks,
            batch_size=args.batch_size,
            verbose=True,
        )

        extraction_time = time.time() - extraction_start
        summary = summarize_graph_documents(graph_docs)
        log(f"  Extraction complete in {extraction_time:.1f}s")
        log(f"    Node types: {summary['node_type_counts']}")

        # Load graph documents
        log("  Loading graph documents into Neo4j...")
        storage.load_graph_documents(graph_docs, include_source=True)

        # Track entity IDs per file (approximate: assign all to first file if multiple)
        all_entity_ids = get_entity_ids_from_graph_docs(graph_docs)
        results["entities_extracted"] = len(all_entity_ids)

        # Distribute entity IDs to files (simplified: all to each file)
        for filename in filenames:
            entity_ids_by_file[filename] = all_entity_ids.copy()

    # Load document chunks
    log("  Loading document chunks...")
    storage.load_document_chunks(chunks)

    # Create/update embeddings
    if is_incremental:
        log("  Adding embeddings incrementally...")
        storage.add_embeddings_incrementally(chunks)
    else:
        log("  Creating vector index...")
        storage.create_vector_index()

    # Update manifest for each processed file
    md_path = Path(config.MARKDOWN_DIR)
    for filename in filenames:
        file_path = md_path / filename
        if file_path.exists():
            content_hash = compute_file_hash(file_path)
            chunk_ids = [c.metadata["chunk_id"] for c in chunks_by_file.get(filename, [])]
            entity_ids = entity_ids_by_file.get(filename, [])
            manifest.update_file_record(filename, content_hash, chunk_ids, entity_ids)

    return results


def handle_deleted_files(
    deleted_files: List[str],
    storage: GraphStorage,
    manifest: ManifestManager,
):
    """
    Clean up chunks and entities from deleted files.

    Args:
        deleted_files: List of deleted filenames
        storage: GraphStorage instance
        manifest: ManifestManager instance
    """
    if not deleted_files:
        return

    log(f"  Cleaning up {len(deleted_files)} deleted file(s)...")

    # Collect all chunk IDs and entity IDs to remove
    all_chunk_ids = []
    all_entity_ids = []

    for filename in deleted_files:
        chunk_ids = manifest.get_chunk_ids_for_file(filename)
        entity_ids = manifest.get_entity_ids_for_file(filename)
        all_chunk_ids.extend(chunk_ids)
        all_entity_ids.extend(entity_ids)
        manifest.remove_file_record(filename)

    # Remove chunks from database
    if all_chunk_ids:
        storage.remove_document_chunks(all_chunk_ids)

    # Remove entities (may leave orphans if shared)
    if all_entity_ids:
        storage.remove_entities_by_ids(all_entity_ids)

    # Clean up any orphaned entities
    storage.cleanup_orphaned_entities()


def handle_modified_files(
    modified_files: List[str],
    storage: GraphStorage,
    manifest: ManifestManager,
):
    """
    Clean up old chunks from modified files before re-processing.

    Args:
        modified_files: List of modified filenames
        storage: GraphStorage instance
        manifest: ManifestManager instance
    """
    if not modified_files:
        return

    log(f"  Cleaning up old data from {len(modified_files)} modified file(s)...")

    # Collect all chunk IDs to remove
    all_chunk_ids = []
    all_entity_ids = []

    for filename in modified_files:
        chunk_ids = manifest.get_chunk_ids_for_file(filename)
        entity_ids = manifest.get_entity_ids_for_file(filename)
        all_chunk_ids.extend(chunk_ids)
        all_entity_ids.extend(entity_ids)

    # Remove old chunks
    if all_chunk_ids:
        storage.remove_document_chunks(all_chunk_ids)

    # Remove old entities
    if all_entity_ids:
        storage.remove_entities_by_ids(all_entity_ids)


def run_full_build(args):
    """Run a full build (ignoring manifest)."""
    total_steps = 7 if not args.skip_extraction else 5
    start_time = time.time()

    log("=" * 60)
    log("GraphRAG Knowledge Graph Builder - FULL BUILD")
    log("=" * 60)

    # Step 1: Load documents
    log_step(1, total_steps, "Loading markdown files...")
    documents = load_markdown_files()
    log(f"  Loaded {len(documents)} files")

    # Step 2: Chunk documents
    log_step(2, total_steps, "Chunking documents by headers...")
    chunks = chunk_documents(documents, use_stable_ids=True)
    log(f"  Created {len(chunks)} chunks")

    # Show sample chunks
    log("\n  Sample chunks:")
    for chunk in chunks[:3]:
        log(f"    {get_chunk_summary(chunk)}")

    # Step 3: Connect to Neo4j
    log_step(3, total_steps, "Connecting to Neo4j...")
    storage = GraphStorage()
    log("  Connected successfully!")

    # Clear if requested
    if args.clear:
        confirm = input("\n  This will DELETE all data in the database. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            storage.clear_database(confirm=True)
            log("  Database cleared")
        else:
            log("  Clear aborted.")
            return

    current_step = 4

    # Step 4: Extract knowledge graph (unless skipped)
    graph_docs = []
    if not args.skip_extraction:
        log_step(current_step, total_steps, f"Extracting knowledge graph via LLM (batch_size={args.batch_size})...")
        log("  This may take several minutes depending on document size...")

        extraction_start = time.time()
        graph_docs = extract_graph_from_documents(
            chunks,
            batch_size=args.batch_size,
            verbose=True,
        )
        extraction_time = time.time() - extraction_start

        summary = summarize_graph_documents(graph_docs)
        log(f"\n  Extraction complete in {extraction_time:.1f}s")
        log(f"    Node types: {summary['node_type_counts']}")
        log(f"    Relationship types: {summary['relationship_type_counts']}")

        print_sample_extractions(graph_docs, max_samples=5)

        # Step 5: Load graph documents
        current_step += 1
        log_step(current_step, total_steps, "Loading graph documents into Neo4j...")
        load_start = time.time()
        storage.load_graph_documents(graph_docs, include_source=True)
        log(f"  Loaded in {time.time() - load_start:.1f}s")

        current_step += 1
    else:
        log_step(current_step, total_steps, "Skipping graph extraction (--skip-extraction flag)")
        current_step += 1

    # Step 6: Load document chunks
    log_step(current_step, total_steps, "Loading document chunks for vector search...")
    chunk_start = time.time()
    storage.load_document_chunks(chunks)
    log(f"  Loaded {len(chunks)} chunks in {time.time() - chunk_start:.1f}s")
    current_step += 1

    # Step 7: Create vector index
    log_step(current_step, total_steps, "Creating vector embeddings & index...")
    vector_start = time.time()
    storage.create_vector_index()
    log(f"  Vector index created in {time.time() - vector_start:.1f}s")
    current_step += 1

    # Create fulltext index
    log("  Creating fulltext index...")
    storage.create_fulltext_index()

    # Update manifest with all files
    manifest = ManifestManager()
    md_path = Path(config.MARKDOWN_DIR)

    # Group chunks by file
    chunks_by_file = {}
    for chunk in chunks:
        filename = chunk.metadata.get("filename", "unknown")
        if filename not in chunks_by_file:
            chunks_by_file[filename] = []
        chunks_by_file[filename].append(chunk)

    # Get entity IDs from graph docs
    entity_ids = get_entity_ids_from_graph_docs(graph_docs)

    for doc in documents:
        filename = doc.metadata["filename"]
        file_path = md_path / filename
        content_hash = compute_file_hash(file_path)
        chunk_ids = [c.metadata["chunk_id"] for c in chunks_by_file.get(filename, [])]
        manifest.update_file_record(filename, content_hash, chunk_ids, entity_ids)

    manifest.save()
    log(f"\n  Manifest saved with {len(manifest.files)} file records")

    # Final statistics
    total_time = time.time() - start_time
    log("\n" + "=" * 60)
    log(f"Build Complete! (Total time: {total_time:.1f}s)")
    log("=" * 60)

    print_statistics(storage)


def run_incremental_build(args):
    """Run an incremental build using the manifest."""
    start_time = time.time()

    log("=" * 60)
    log("GraphRAG Knowledge Graph Builder - INCREMENTAL UPDATE")
    log("=" * 60)

    # Load manifest and detect changes
    log("\nDetecting changes...")
    manifest = ManifestManager()
    changes = manifest.detect_changes()

    log(f"  Manifest: {len(manifest.files)} file(s) tracked")
    log(f"  Changes: {changes.summary()}")

    if changes.new_files:
        log(f"    New: {changes.new_files}")
    if changes.modified_files:
        log(f"    Modified: {changes.modified_files}")
    if changes.deleted_files:
        log(f"    Deleted: {changes.deleted_files}")

    # Dry-run mode: just show changes and exit
    if args.dry_run:
        log("\n[DRY RUN] No changes made.")
        return

    # No changes: nothing to do
    if not changes.has_changes:
        log("\nNo changes detected. Knowledge graph is up to date.")
        return

    # Connect to Neo4j
    log("\nConnecting to Neo4j...")
    storage = GraphStorage()
    log("  Connected successfully!")

    # Handle deleted files first
    if changes.deleted_files:
        log("\nProcessing deleted files...")
        handle_deleted_files(changes.deleted_files, storage, manifest)

    # Handle modified files (clean up old data)
    if changes.modified_files:
        log("\nProcessing modified files...")
        handle_modified_files(changes.modified_files, storage, manifest)

    # Process new and modified files together
    files_to_process = changes.new_files + changes.modified_files
    if files_to_process:
        log(f"\nProcessing {len(files_to_process)} file(s)...")
        results = process_files(
            files_to_process,
            storage,
            manifest,
            args,
            is_incremental=True,
        )
        log(f"  Processed: {results['files_processed']} files, {results['chunks_created']} chunks")

    # Ensure indexes exist
    log("\nEnsuring indexes exist...")
    storage.create_fulltext_index()

    # Save manifest
    manifest.save()
    log(f"Manifest saved with {len(manifest.files)} file records")

    # Final statistics
    total_time = time.time() - start_time
    log("\n" + "=" * 60)
    log(f"Incremental Update Complete! (Total time: {total_time:.1f}s)")
    log("=" * 60)

    print_statistics(storage)


def print_statistics(storage: GraphStorage):
    """Print database statistics."""
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

    log("\nKnowledge graph is ready for querying!")
    log("  Run: streamlit run app.py")


def main():
    parser = argparse.ArgumentParser(
        description="Build or update the knowledge graph from markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_graph.py              # Incremental update (default)
  python scripts/build_graph.py --full       # Force full rebuild
  python scripts/build_graph.py --dry-run    # Show what would change
  python scripts/build_graph.py --clear      # Clear DB and rebuild
        """
    )
    parser.add_argument("--clear", action="store_true",
                        help="Clear database before loading (implies --full)")
    parser.add_argument("--full", action="store_true",
                        help="Force full rebuild (ignore manifest)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without making changes")
    parser.add_argument("--skip-extraction", action="store_true",
                        help="Skip LLM graph extraction")
    parser.add_argument("--batch-size", type=int, default=3,
                        help="Batch size for LLM extraction (default: 3)")
    args = parser.parse_args()

    # --clear implies --full
    if args.clear:
        args.full = True

    # Decide which mode to run
    if args.full:
        run_full_build(args)
    else:
        run_incremental_build(args)


if __name__ == "__main__":
    main()
