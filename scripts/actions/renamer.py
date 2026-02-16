"""File renamer action module."""
import os
import re
from pathlib import Path
from typing import Union, Optional


class Renamer:
    """Handles file rename operations."""

    def rename(
        self,
        file_path: Union[str, Path],
        replace: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        separator: str = "-",
    ) -> Path:
        """
        Rename a file based on specified rules.

        Args:
            file_path: File to rename
            replace: Regex replacement pattern
            prefix: Prefix to add
            suffix: Suffix to add (before extension)
            separator: Separator to use between parts

        Returns:
            New file path

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        name = file_path.stem
        ext = file_path.suffix

        # Apply regex replacement
        if replace:
            name = re.sub(r"（(\d+)）|\((\d+)\)", replace, name)
            name = re.sub(r"\s*\(\d+\)\s*", replace, name)
            name = re.sub(r"\s*\[\d+\]\s*", replace, name)

        # Apply prefix
        if prefix:
            name = f"{prefix}{separator}{name}"

        # Apply suffix
        if suffix:
            name = f"{name}{separator}{suffix}"

        # Clean up multiple separators
        name = re.sub(rf"{re.escape(separator)}+", separator, name)
        name = name.strip(separator)

        # New path
        new_path = file_path.parent / f"{name}{ext}"

        # Rename
        if new_path != file_path:
            file_path.rename(new_path)

        return new_path

    def clean_garbled(self, file_path: Union[str, Path]) -> Path:
        """
        Attempt to clean garbled characters from filename.

        Args:
            file_path: File to clean

        Returns:
            New file path
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Common garbled patterns and their cleaned versions
        # This is a basic implementation - could be enhanced

        name = file_path.stem
        ext = file_path.suffix

        # Remove common garbled patterns
        name = re.sub(r"[\u0000-\u001f\u007f-\u009f]", "", name)  # Control chars
        name = re.sub(r"[™©®]", "", name)  # Common symbols that cause issues

        # Clean up spaces
        name = re.sub(r"\s+", " ", name)
        name = name.strip()

        new_path = file_path.parent / f"{name}{ext}"

        if new_path != file_path:
            file_path.rename(new_path)

        return new_path
