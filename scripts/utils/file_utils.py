"""File utilities."""
import os
from pathlib import Path
from typing import List, Union


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    return Path(file_path).stat().st_size


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def list_files(
    directory: Union[str, Path],
    recursive: bool = True,
    include_hidden: bool = False,
) -> List[Path]:
    """List all files in a directory."""
    directory = Path(directory)
    if not directory.exists():
        return []

    files = []
    pattern = "**/*" if recursive else "*"

    for item in directory.glob(pattern):
        if item.is_file():
            if not include_hidden and item.name.startswith("."):
                continue
            files.append(item)

    return sorted(files)


def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure directory exists, create if needed."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def is_text_file(file_path: Union[str, Path]) -> bool:
    """Check if a file is likely a text file."""
    text_extensions = {
        ".txt", ".md", ".json", ".yaml", ".yml", ".xml", ".csv",
        ".py", ".js", ".ts", ".html", ".css", ".scss", ".less",
        ".sh", ".bash", ".zsh", ".fish",
        ".c", ".cpp", ".h", ".hpp", ".java", ".go", ".rs",
        ".sql", ".graphql", ".proto",
    }
    return Path(file_path).suffix.lower() in text_extensions
