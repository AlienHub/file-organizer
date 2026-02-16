"""Rule parsing module for File Organizer."""
import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Condition:
    """Condition for matching files."""
    path: Optional[str] = None
    extension: Optional[List[str]] = None
    pattern: Optional[str] = None
    size_gt: Optional[int] = None  # bytes
    size_lt: Optional[int] = None
    name_pattern: Optional[str] = None

    def matches(self, file_path: Path) -> bool:
        """Check if file matches this condition."""
        # Check path
        if self.path:
            path_pattern = os.path.expanduser(self.path)
            if not str(file_path).startswith(path_pattern):
                return False

        # Check extension
        if self.extension:
            ext = file_path.suffix.lower().lstrip(".")
            if ext not in [e.lower().lstrip(".") for e in self.extension]:
                return False

        # Check name pattern (regex)
        if self.name_pattern:
            if not re.search(self.name_pattern, file_path.name):
                return False

        # Check content pattern (regex in filename)
        if self.pattern:
            if not re.search(self.pattern, file_path.name):
                return False

        # Check size
        if self.size_gt or self.size_lt:
            try:
                size = file_path.stat().st_size
                if self.size_gt and size <= self.size_gt:
                    return False
                if self.size_lt and size >= self.size_lt:
                    return False
            except OSError:
                return False

        return True


@dataclass
class Action:
    """Action to perform on matched files."""
    move: Optional[str] = None
    create_if_missing: bool = False
    rename: Optional[str] = None
    replace: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    separator: str = "-"
    tag: Optional[Dict[str, str]] = None


@dataclass
class Rule:
    """A rule for file organization."""
    name: str
    condition: Condition
    action: Action
    enabled: bool = True


@dataclass
class DuplicateRule:
    """Rule for handling duplicate files."""
    name: str
    check_by: str = "content"  # "content" or "name"
    action: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


def parse_size(size_str: str) -> int:
    """Parse size string like '100MB' to bytes."""
    size_str = size_str.strip().upper()
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
        "TB": 1024 * 1024 * 1024 * 1024,
    }
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                return int(float(size_str[:-len(unit)]) * multiplier)
            except ValueError:
                break
    # Try parsing as raw bytes
    try:
        return int(size_str)
    except ValueError:
        return 0


def parse_condition(cond_data: Dict[str, Any]) -> Condition:
    """Parse condition from dict."""
    size_gt = cond_data.get("size_gt")
    if isinstance(size_gt, str):
        size_gt = parse_size(size_gt)

    size_lt = cond_data.get("size_lt")
    if isinstance(size_lt, str):
        size_lt = parse_size(size_lt)

    return Condition(
        path=cond_data.get("path"),
        extension=cond_data.get("extension"),
        pattern=cond_data.get("pattern"),
        name_pattern=cond_data.get("name_pattern"),
        size_gt=size_gt,
        size_lt=size_lt,
    )


def parse_action(action_data: Dict[str, Any]) -> Action:
    """Parse action from dict."""
    tag_data = action_data.get("tag")
    return Action(
        move=action_data.get("move"),
        create_if_missing=action_data.get("create_if_missing", False),
        rename=action_data.get("rename"),
        replace=action_data.get("replace"),
        prefix=action_data.get("prefix"),
        suffix=action_data.get("suffix"),
        separator=action_data.get("separator", "-"),
        tag=tag_data if tag_data else None,
    )


def parse_rule(rule_data: Dict[str, Any]) -> Rule:
    """Parse rule from dict."""
    return Rule(
        name=rule_data.get("name", "Unnamed Rule"),
        condition=parse_condition(rule_data.get("condition", {})),
        action=parse_action(rule_data.get("action", {})),
        enabled=rule_data.get("enabled", True),
    )


def parse_duplicate_rule(rule_data: Dict[str, Any]) -> DuplicateRule:
    """Parse duplicate rule from dict."""
    return DuplicateRule(
        name=rule_data.get("name", "Unnamed Duplicate Rule"),
        check_by=rule_data.get("check_by", "content"),
        action=rule_data.get("action", {}),
        enabled=rule_data.get("enabled", True),
    )


class RuleParser:
    """Parser for YAML rule files."""

    def __init__(self, rules_dir: Path):
        self.rules_dir = rules_dir

    def load_move_rules(self) -> List[Rule]:
        """Load move rules from move.yaml."""
        return self._load_rules("move.yaml", parse_rule)

    def load_rename_rules(self) -> List[Rule]:
        """Load rename rules from rename.yaml."""
        return self._load_rules("rename.yaml", parse_rule)

    def load_tag_rules(self) -> List[Rule]:
        """Load tag rules from tag.yaml."""
        return self._load_rules("tag.yaml", parse_rule)

    def load_duplicate_rules(self) -> List[DuplicateRule]:
        """Load duplicate rules from duplicate.yaml."""
        return self._load_rules("duplicate.yaml", parse_duplicate_rule)

    def _load_rules(self, filename: str, parser: Callable) -> List:
        """Load rules from a YAML file."""
        rule_file = self.rules_dir / filename
        if not rule_file.exists():
            return []

        with open(rule_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        rules = []
        for rule_data in data.get("rules", []):
            try:
                rules.append(parser(rule_data))
            except Exception as e:
                print(f"Error parsing rule {rule_data.get('name')}: {e}")

        return [r for r in rules if r.enabled]

    def load_all_rules(self) -> Dict[str, List]:
        """Load all rules."""
        return {
            "move": self.load_move_rules(),
            "rename": self.load_rename_rules(),
            "tag": self.load_tag_rules(),
            "duplicate": self.load_duplicate_rules(),
        }
