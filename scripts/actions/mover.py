"""File mover action module."""
import os
import shutil
from pathlib import Path
from typing import Union


class Mover:
    """Handles file moving operations."""

    def move(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Move a file to destination.

        Args:
            source: Source file path
            destination: Destination directory or file path

        Returns:
            New file path

        Raises:
            FileNotFoundError: If source doesn't exist
            FileExistsError: If destination already exists
        """
        source = Path(source)
        destination = Path(destination)

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        # If destination is a directory, move file into it
        if destination.is_dir():
            destination = destination / source.name

        # Create parent directory if needed
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(source), str(destination))

        return destination

    def copy(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Copy a file to destination.

        Args:
            source: Source file path
            destination: Destination directory or file path

        Returns:
            New file path
        """
        source = Path(source)
        destination = Path(destination)

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        # If destination is a directory, copy file into it
        if destination.is_dir():
            destination = destination / source.name

        # Create parent directory if needed
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(str(source), str(destination))

        return destination
