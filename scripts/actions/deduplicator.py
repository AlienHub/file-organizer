"""Deduplicator action module."""
import hashlib
from pathlib import Path
from typing import List, Union, Dict, Any
from collections import defaultdict


class Deduplicator:
    """Handles duplicate file detection and handling."""

    def find_duplicates(
        self,
        files: List[Path],
        check_by: str = "content",
    ) -> List[List[Path]]:
        """
        Find duplicate files.

        Args:
            files: List of files to check
            check_by: "content" (hash) or "name"

        Returns:
            List of duplicate groups (each group is a list of paths)
        """
        if check_by == "name":
            return self._find_by_name(files)
        else:
            return self._find_by_content(files)

    def _find_by_name(self, files: List[Path]) -> List[List[Path]]:
        """Find duplicates by filename."""
        groups = defaultdict(list)

        for file_path in files:
            groups[file_path.name].append(file_path)

        # Return only groups with more than one file
        return [paths for paths in groups.values() if len(paths) > 1]

    def _find_by_content(self, files: List[Path]) -> List[List[Path]]:
        """Find duplicates by content hash."""
        hash_groups = defaultdict(list)

        for file_path in files:
            if not file_path.is_file():
                continue

            try:
                file_hash = self._hash_file(file_path)
                hash_groups[file_hash].append(file_path)
            except Exception:
                # Skip files that can't be read
                continue

        # Return only groups with more than one file
        return [paths for paths in hash_groups.values() if len(paths) > 1]

    def _hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()

    def handle_duplicates(
        self,
        duplicate_group: List[Path],
        keep: str = "newest",
        tag_duplicates: bool = False,
        duplicate_label: str = "重复",
    ) -> None:
        """
        Handle a group of duplicate files.

        Args:
            duplicate_group: List of duplicate file paths
            keep: Which file to keep ("newest", "oldest", "first")
            tag_duplicates: Whether to tag duplicates
            duplicate_label: Label to add to duplicates
        """
        if len(duplicate_group) < 2:
            return

        # Determine which file to keep
        if keep == "newest":
            keep_file = max(duplicate_group, key=lambda p: p.stat().st_mtime)
        elif keep == "oldest":
            keep_file = min(duplicate_group, key=lambda p: p.stat().st_mtime)
        else:  # "first"
            keep_file = duplicate_group[0]

        # Handle remaining files
        for file_path in duplicate_group:
            if file_path == keep_file:
                continue

            if tag_duplicates:
                # Tag the duplicate instead of deleting
                from .tagger import Tagger
                tagger = Tagger()
                tagger.add_tag(file_path, label=duplicate_label)
            else:
                # Move to trash or delete
                self._move_to_trash(file_path)

    def _move_to_trash(self, file_path: Path) -> None:
        """Move file to trash."""
        import platform
        import subprocess

        if platform.system() == "Darwin":
            # Use AppleScript to move to trash
            script = f'''
            tell application "Finder"
                delete POSIX file "{file_path}"
            end tell
            '''
            subprocess.run(["osascript", "-e", script], check=False)
        else:
            # Just delete on other platforms
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information for duplicate analysis."""
        stat = file_path.stat()
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
        }
