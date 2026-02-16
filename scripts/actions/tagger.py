"""Mac Tag action module."""
import os
import platform
import subprocess
from pathlib import Path
from typing import Union, Optional, List, Dict


# Mac Tag colors
TAG_COLORS = {
    "gray": "gray",
    "red": "red",
    "orange": "orange",
    "yellow": "yellow",
    "green": "green",
    "blue": "blue",
    "purple": "purple",
}


class Tagger:
    """Handles Mac Finder tags."""

    def __init__(self):
        self.is_macos = platform.system() == "Darwin"

    def add_tag(
        self,
        file_path: Union[str, Path],
        color: Optional[str] = None,
        label: Optional[str] = None,
    ) -> bool:
        """
        Add a tag to a file.

        Args:
            file_path: File to tag
            color: Tag color (gray, red, orange, yellow, green, blue, purple)
            label: Tag label text

        Returns:
            True if successful
        """
        if not self.is_macos:
            print(f"Warning: Mac Tags not supported on {platform.system()}")
            return False

        file_path = Path(file_path)
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            return False

        tags = []

        # Add color tag
        if color and color.lower() in TAG_COLORS:
            tags.append(TAG_COLORS[color.lower()])

        # Add label tag
        if label:
            tags.append(label)

        if not tags:
            return False

        try:
            # Use xattr to set Finder tags (native macOS way)
            tag_string = ", ".join(tags)
            result = subprocess.run(
                ["xattr", "-w", "com.apple.metadata:_kMDItemUserTags",
                 self._create_plist(tags), str(file_path)],
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                # Fallback: use osascript
                self._add_tag_osascript(file_path, tags)

            return True

        except Exception as e:
            print(f"Error adding tag: {e}")
            return False

    def _create_plist(self, tags: List[str]) -> str:
        """Create plist string for tags."""
        import plistlib
        data = plistlib.dumps(tags)
        import base64
        return base64.b64encode(data).decode()

    # 标签颜色索引: 0=无, 1=灰, 2=红, 3=橙, 4=黄, 5=绿, 6=蓝, 7=紫
    TAG_COLOR_INDEX = {
        "gray": 1,
        "red": 2,
        "orange": 3,
        "yellow": 4,
        "green": 5,
        "blue": 6,
        "purple": 7,
    }

    def _add_tag_osascript(self, file_path: Path, tags: List[str]) -> None:
        """Add tag using AppleScript (fallback method)."""
        # 找出颜色标签
        color_index = 0
        for tag in tags:
            if tag.lower() in self.TAG_COLOR_INDEX:
                color_index = self.TAG_COLOR_INDEX[tag.lower()]
                break

        # 获取完整绝对路径
        abs_path = file_path.resolve()

        # 使用正确的 AppleScript 设置标签颜色
        script = f'''
        tell application "Finder"
            set theFile to POSIX file "{abs_path}" as alias
            set label index of theFile to {color_index}
        end tell
        '''
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)

    def remove_tag(
        self,
        file_path: Union[str, Path],
        label: Optional[str] = None,
    ) -> bool:
        """
        Remove tags from a file.

        Args:
            file_path: File to untag
            label: Specific label to remove (None removes all)

        Returns:
            True if successful
        """
        if not self.is_macos:
            return False

        file_path = Path(file_path)
        if not file_path.exists():
            return False

        try:
            # Clear all tags
            subprocess.run(
                ["xattr", "-d", "com.apple.metadata:_kMDItemUserTags", str(file_path)],
                capture_output=True,
                check=False,
            )
            return True

        except Exception as e:
            print(f"Error removing tag: {e}")
            return False

    def get_tags(self, file_path: Union[str, Path]) -> List[str]:
        """
        Get tags from a file.

        Args:
            file_path: File to read tags from

        Returns:
            List of tag strings
        """
        if not self.is_macos:
            return []

        file_path = Path(file_path)
        if not file_path.exists():
            return []

        try:
            result = subprocess.run(
                ["xattr", "-p", "com.apple.metadata:_kMDItemUserTags", str(file_path)],
                capture_output=True,
                check=False,
            )

            if result.returncode == 0 and result.stdout:
                import base64
                import plistlib
                data = base64.b64decode(result.stdout)
                return plistlib.loads(data)

        except Exception:
            pass

        return []
