"""
Manifest Management for Incremental Knowledge Graph Updates

Tracks processed files via SHA256 content hashing to enable incremental updates.
Only new/modified files are re-processed; deleted files trigger cleanup.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional, Set

import config


@dataclass
class FileRecord:
    """Record of a processed file."""
    filename: str
    content_hash: str
    chunk_ids: List[str] = field(default_factory=list)
    entity_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "FileRecord":
        return cls(
            filename=data["filename"],
            content_hash=data["content_hash"],
            chunk_ids=data.get("chunk_ids", []),
            entity_ids=data.get("entity_ids", []),
        )


@dataclass
class ChangeSet:
    """Set of changes detected between disk and manifest."""
    new_files: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    deleted_files: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.new_files or self.modified_files or self.deleted_files)

    def summary(self) -> str:
        parts = []
        if self.new_files:
            parts.append(f"{len(self.new_files)} new")
        if self.modified_files:
            parts.append(f"{len(self.modified_files)} modified")
        if self.deleted_files:
            parts.append(f"{len(self.deleted_files)} deleted")
        return ", ".join(parts) if parts else "No changes"


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of file contents.

    Args:
        file_path: Path to the file.

    Returns:
        Hex digest of the SHA256 hash.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks for memory efficiency with large files
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


class ManifestManager:
    """
    Manages the build manifest for incremental updates.

    The manifest tracks:
    - File content hashes (to detect modifications)
    - Chunk IDs created from each file (for cleanup on modification/deletion)
    - Entity IDs extracted from each file (for orphan cleanup)
    """

    DEFAULT_MANIFEST_PATH = ".manifest.json"

    def __init__(self, manifest_path: Optional[str] = None):
        """
        Initialize the manifest manager.

        Args:
            manifest_path: Path to manifest file. Defaults to .manifest.json in project root.
        """
        if manifest_path is None:
            # Default to project root
            project_root = Path(config.MARKDOWN_DIR).parent
            self.manifest_path = project_root / self.DEFAULT_MANIFEST_PATH
        else:
            self.manifest_path = Path(manifest_path)

        self.files: Dict[str, FileRecord] = {}
        self._load()

    def _load(self):
        """Load manifest from disk if it exists."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.files = {
                        filename: FileRecord.from_dict(record)
                        for filename, record in data.get("files", {}).items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not parse manifest, starting fresh: {e}")
                self.files = {}
        else:
            self.files = {}

    def save(self):
        """Save manifest to disk."""
        data = {
            "version": 1,
            "files": {
                filename: record.to_dict()
                for filename, record in self.files.items()
            }
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def detect_changes(self, directory: Optional[str] = None) -> ChangeSet:
        """
        Detect changes between disk files and manifest.

        Args:
            directory: Directory containing markdown files.
                       Defaults to config.MARKDOWN_DIR.

        Returns:
            ChangeSet with new, modified, and deleted files.
        """
        if directory is None:
            directory = config.MARKDOWN_DIR

        md_path = Path(directory)
        if not md_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Get current files on disk
        disk_files: Dict[str, str] = {}  # filename -> hash
        for file_path in md_path.glob("*.md"):
            disk_files[file_path.name] = compute_file_hash(file_path)

        # Get files in manifest
        manifest_files: Set[str] = set(self.files.keys())
        disk_file_names: Set[str] = set(disk_files.keys())

        changes = ChangeSet()

        # New files: on disk but not in manifest
        changes.new_files = sorted(disk_file_names - manifest_files)

        # Deleted files: in manifest but not on disk
        changes.deleted_files = sorted(manifest_files - disk_file_names)

        # Modified files: in both but hash differs
        for filename in manifest_files & disk_file_names:
            if disk_files[filename] != self.files[filename].content_hash:
                changes.modified_files.append(filename)
        changes.modified_files.sort()

        return changes

    def get_file_record(self, filename: str) -> Optional[FileRecord]:
        """Get the record for a specific file."""
        return self.files.get(filename)

    def update_file_record(
        self,
        filename: str,
        content_hash: str,
        chunk_ids: List[str],
        entity_ids: Optional[List[str]] = None,
    ):
        """
        Update or create a file record.

        Args:
            filename: Name of the file.
            content_hash: SHA256 hash of file contents.
            chunk_ids: List of chunk IDs created from this file.
            entity_ids: List of entity IDs extracted from this file.
        """
        self.files[filename] = FileRecord(
            filename=filename,
            content_hash=content_hash,
            chunk_ids=chunk_ids,
            entity_ids=entity_ids or [],
        )

    def remove_file_record(self, filename: str) -> Optional[FileRecord]:
        """
        Remove a file record from the manifest.

        Args:
            filename: Name of the file to remove.

        Returns:
            The removed FileRecord, or None if not found.
        """
        return self.files.pop(filename, None)

    def get_chunk_ids_for_file(self, filename: str) -> List[str]:
        """Get chunk IDs associated with a file."""
        record = self.files.get(filename)
        return record.chunk_ids if record else []

    def get_entity_ids_for_file(self, filename: str) -> List[str]:
        """Get entity IDs associated with a file."""
        record = self.files.get(filename)
        return record.entity_ids if record else []

    def get_all_chunk_ids(self) -> List[str]:
        """Get all chunk IDs across all files."""
        all_ids = []
        for record in self.files.values():
            all_ids.extend(record.chunk_ids)
        return all_ids

    def get_all_entity_ids(self) -> List[str]:
        """Get all entity IDs across all files."""
        all_ids = []
        for record in self.files.values():
            all_ids.extend(record.entity_ids)
        return all_ids


if __name__ == "__main__":
    # Test the manifest system
    manager = ManifestManager()

    print(f"Manifest path: {manager.manifest_path}")
    print(f"Existing records: {len(manager.files)}")

    changes = manager.detect_changes()
    print(f"\nChanges detected: {changes.summary()}")

    if changes.new_files:
        print(f"  New files: {changes.new_files}")
    if changes.modified_files:
        print(f"  Modified files: {changes.modified_files}")
    if changes.deleted_files:
        print(f"  Deleted files: {changes.deleted_files}")
