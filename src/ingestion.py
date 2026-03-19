"""
Step 1: Ingestion & Chunking

Reads Markdown files and chunks them using LangChain's MarkdownHeaderTextSplitter
to preserve strategic structural context based on ## and ### headers.
"""

import os
import re
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

import config


def load_markdown_files(directory: str = None) -> List[Document]:
    """
    Load all .md files from the specified directory.

    Args:
        directory: Path to directory containing markdown files.
                   Defaults to config.MARKDOWN_DIR.

    Returns:
        List of Document objects with content and metadata.
    """
    if directory is None:
        directory = config.MARKDOWN_DIR

    documents = []
    md_path = Path(directory)

    if not md_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Sort files by their numeric prefix for consistent ordering
    md_files = sorted(md_path.glob("*.md"), key=lambda x: x.name)

    for file_path in md_files:
        print(f"Loading: {file_path.name}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract document order and title from filename
        # e.g., "1 - broader-framing.md" -> order=1, title="broader-framing"
        match = re.match(r"(\d+)\s*-\s*(.+)\.md", file_path.name)
        if match:
            doc_order = int(match.group(1))
            doc_title = match.group(2).replace("-", " ").title()
        else:
            doc_order = 0
            doc_title = file_path.stem

        doc = Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "filename": file_path.name,
                "doc_order": doc_order,
                "doc_title": doc_title,
            }
        )
        documents.append(doc)

    print(f"\nLoaded {len(documents)} markdown files.")
    return documents


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Chunk documents using MarkdownHeaderTextSplitter.

    Splits on ## and ### headers to preserve strategic structure.
    Each chunk retains header hierarchy in metadata.

    Args:
        documents: List of Document objects to chunk.

    Returns:
        List of chunked Document objects with header metadata.
    """
    # Define headers to split on (## and ### for our strategic docs)
    headers_to_split_on = [
        ("#", "h1_header"),
        ("##", "h2_header"),
        ("###", "h3_header"),
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,  # Keep headers in content for context
    )

    all_chunks = []

    for doc in documents:
        # Split the document
        chunks = splitter.split_text(doc.page_content)

        # Merge original metadata with header metadata
        for i, chunk in enumerate(chunks):
            # Combine metadata
            combined_metadata = {
                **doc.metadata,
                **chunk.metadata,
                "chunk_index": i,
            }

            # Create a chunk ID for graph linking
            chunk_id = f"{doc.metadata['doc_order']}_{i}"
            combined_metadata["chunk_id"] = chunk_id

            # Create new document with combined metadata
            enriched_chunk = Document(
                page_content=chunk.page_content,
                metadata=combined_metadata
            )
            all_chunks.append(enriched_chunk)

    print(f"Created {len(all_chunks)} chunks from {len(documents)} documents.")
    return all_chunks


def get_chunk_summary(chunk: Document) -> str:
    """Generate a brief summary string for a chunk (for debugging)."""
    headers = []
    if chunk.metadata.get("h1_header"):
        headers.append(chunk.metadata["h1_header"])
    if chunk.metadata.get("h2_header"):
        headers.append(chunk.metadata["h2_header"])
    if chunk.metadata.get("h3_header"):
        headers.append(chunk.metadata["h3_header"])

    header_path = " > ".join(headers) if headers else "No headers"
    preview = chunk.page_content[:100].replace("\n", " ")

    return f"[{chunk.metadata.get('chunk_id', '?')}] {header_path}\n    {preview}..."


if __name__ == "__main__":
    # Test the ingestion pipeline
    docs = load_markdown_files()
    chunks = chunk_documents(docs)

    print("\n--- Sample Chunks ---")
    for chunk in chunks[:5]:
        print(get_chunk_summary(chunk))
        print()
