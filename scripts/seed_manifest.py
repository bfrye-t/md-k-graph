#!/usr/bin/env python3
"""
Seed Manifest from Existing Graph

Bootstraps the manifest by reading existing Document nodes from Neo4j
and matching them to source files. This allows incremental updates to
work correctly when the graph was built before the manifest system existed.

Usage:
    python scripts/seed_manifest.py
    python scripts/seed_manifest.py --dry-run
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.manifest import ManifestManager, compute_file_hash
from src.graph_storage import GraphStorage
import config


def get_chunks_from_graph(storage: GraphStorage) -> list:
    """Query existing Document chunks from Neo4j."""
    query = """
    MATCH (d:Document)
    RETURN d.chunk_id AS chunk_id,
           d.source AS source,
           d.doc_title AS doc_title
    """
    return storage.graph.query(query)


def get_entities_from_graph(storage: GraphStorage) -> list:
    """Query existing Entity nodes from Neo4j."""
    query = """
    MATCH (n:__Entity__)
    RETURN n.id AS id
    """
    return storage.graph.query(query)


def main():
    parser = argparse.ArgumentParser(
        description="Seed manifest from existing Neo4j graph"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be written without saving")
    args = parser.parse_args()

    print("=" * 60)
    print("Seed Manifest from Existing Graph")
    print("=" * 60)

    # Connect to Neo4j
    print("\nConnecting to Neo4j...")
    storage = GraphStorage()
    print("  Connected!")

    # Get existing chunks
    print("\nQuerying existing Document chunks...")
    chunks = get_chunks_from_graph(storage)
    print(f"  Found {len(chunks)} chunks in graph")

    if not chunks:
        print("\nNo chunks found in graph. Nothing to seed.")
        return

    # Get existing entities
    print("\nQuerying existing Entity nodes...")
    entities = get_entities_from_graph(storage)
    entity_ids = [e["id"] for e in entities if e["id"]]
    print(f"  Found {len(entity_ids)} entities in graph")

    # Group chunks by source file
    chunks_by_file = defaultdict(list)
    for chunk in chunks:
        source = chunk.get("source", "")
        chunk_id = chunk.get("chunk_id", "")
        if source and chunk_id:
            # Extract filename from full path
            filename = Path(source).name
            chunks_by_file[filename].append(chunk_id)

    print(f"\nFiles with chunks in graph:")
    for filename, chunk_ids in sorted(chunks_by_file.items()):
        print(f"  {filename}: {len(chunk_ids)} chunks")

    # Get files on disk
    md_path = Path(config.MARKDOWN_DIR)
    disk_files = {f.name for f in md_path.glob("*.md")}

    print(f"\nFiles on disk: {len(disk_files)}")

    # Find files in graph but not on disk (deleted)
    graph_files = set(chunks_by_file.keys())
    deleted = graph_files - disk_files
    if deleted:
        print(f"  Warning: {len(deleted)} files in graph but not on disk: {deleted}")

    # Find files on disk but not in graph (new)
    new_files = disk_files - graph_files
    if new_files:
        print(f"  New files (not in graph): {sorted(new_files)}")

    # Build manifest
    print("\nBuilding manifest...")
    manifest = ManifestManager()

    # Add records for files that exist both in graph and on disk
    for filename in sorted(graph_files & disk_files):
        file_path = md_path / filename
        content_hash = compute_file_hash(file_path)
        chunk_ids = chunks_by_file[filename]

        # Associate all entities with each file (simplified approach)
        # In practice, entities might be shared across files
        manifest.update_file_record(
            filename=filename,
            content_hash=content_hash,
            chunk_ids=chunk_ids,
            entity_ids=entity_ids,  # All entities associated with all files
        )
        print(f"  Added: {filename} ({len(chunk_ids)} chunks, hash: {content_hash[:8]}...)")

    # Summary
    print(f"\nManifest summary:")
    print(f"  Files tracked: {len(manifest.files)}")
    print(f"  Files to process on next run: {len(new_files)}")
    if new_files:
        print(f"    New files: {sorted(new_files)}")

    # Save or show dry-run
    if args.dry_run:
        print(f"\n[DRY RUN] Would save manifest to: {manifest.manifest_path}")
    else:
        manifest.save()
        print(f"\nManifest saved to: {manifest.manifest_path}")
        print("\nYou can now run incremental updates:")
        print("  python scripts/build_graph.py --dry-run  # Preview")
        print("  python scripts/build_graph.py            # Process new files only")


if __name__ == "__main__":
    main()
