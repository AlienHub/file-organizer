"""Runner module for executing file organization tasks."""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from parser import Rule, DuplicateRule, RuleParser
from actions.mover import Mover
from actions.renamer import Renamer
from actions.tagger import Tagger
from actions.deduplicator import Deduplicator


class Operation:
    """Represents a single operation to be performed."""

    def __init__(self, rule_name: str, operation_type: str, source: Path, details: Dict[str, Any]):
        self.rule_name = rule_name
        self.operation_type = operation_type
        self.source = source
        self.details = details
        self.executed = False
        self.success = False
        self.error: Optional[str] = None

    def __repr__(self) -> str:
        return f"Operation({self.operation_type}: {self.source} -> {self.details})"


class OperationResult:
    """Result of an operation execution."""

    def __init__(self, operation: Operation):
        self.operation = operation
        self.timestamp = datetime.now()


class Runner:
    """Executes file organization rules."""

    def __init__(self, rules_dir: Path, logs_dir: Path, dry_run: bool = True):
        self.rules_dir = rules_dir
        self.logs_dir = logs_dir
        self.dry_run = dry_run

        self.parser = RuleParser(rules_dir)
        self.operations: List[Operation] = []
        self.results: List[OperationResult] = []

        # Initialize action handlers
        self.mover = Mover()
        self.renamer = Renamer()
        self.tagger = Tagger()
        self.deduplicator = Deduplicator()

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging to file."""
        log_file = self.logs_dir / "operation.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

    def scan_and_plan(self) -> List[Operation]:
        """Scan directories and plan operations based on rules."""
        self.operations = []
        rules = self.parser.load_all_rules()

        # Process move rules
        for rule in rules.get("move", []):
            self._plan_move_operations(rule)

        # Process rename rules
        for rule in rules.get("rename", []):
            self._plan_rename_operations(rule)

        # Process tag rules
        for rule in rules.get("tag", []):
            self._plan_tag_operations(rule)

        # Process duplicate rules
        for rule in rules.get("duplicate", []):
            self._plan_duplicate_operations(rule)

        return self.operations

    def _scan_directory(self, path: str) -> List[Path]:
        """Scan directory for files."""
        scan_path = Path(os.path.expanduser(path))
        if not scan_path.exists():
            return []

        files = []
        if scan_path.is_file():
            files.append(scan_path)
        else:
            for item in scan_path.rglob("*"):
                if item.is_file():
                    files.append(item)

        return files

    def _plan_move_operations(self, rule: Rule) -> None:
        """Plan move operations for a rule."""
        if not rule.condition.path:
            return

        files = self._scan_directory(rule.condition.path)

        for file_path in files:
            if rule.condition.matches(file_path):
                dest = os.path.expanduser(rule.action.move)
                operation = Operation(
                    rule_name=rule.name,
                    operation_type="move",
                    source=file_path,
                    details={
                        "destination": dest,
                        "create_if_missing": rule.action.create_if_missing,
                        "tag": rule.action.tag,
                    },
                )
                self.operations.append(operation)

    def _plan_rename_operations(self, rule: Rule) -> None:
        """Plan rename operations for a rule."""
        # Scan common locations if no specific path
        scan_paths = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
        ]

        for scan_path in scan_paths:
            files = self._scan_directory(scan_path)
            for file_path in files:
                if rule.condition.matches(file_path):
                    operation = Operation(
                        rule_name=rule.name,
                        operation_type="rename",
                        source=file_path,
                        details={
                            "replace": rule.action.replace,
                            "prefix": rule.action.prefix,
                            "suffix": rule.action.suffix,
                            "separator": rule.action.separator,
                        },
                    )
                    self.operations.append(operation)

    def _plan_tag_operations(self, rule: Rule) -> None:
        """Plan tag operations for a rule."""
        scan_paths = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
        ]

        for scan_path in scan_paths:
            files = self._scan_directory(scan_path)
            for file_path in files:
                if rule.condition.matches(file_path):
                    operation = Operation(
                        rule_name=rule.name,
                        operation_type="tag",
                        source=file_path,
                        details=rule.action.tag or {},
                    )
                    self.operations.append(operation)

    def _plan_duplicate_operations(self, rule: DuplicateRule) -> None:
        """Plan duplicate detection operations."""
        scan_paths = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
        ]

        all_files = []
        for scan_path in scan_paths:
            all_files.extend(self._scan_directory(scan_path))

        duplicates = self.deduplicator.find_duplicates(
            all_files,
            check_by=rule.check_by,
        )

        for duplicate_group in duplicates:
            operation = Operation(
                rule_name=rule.name,
                operation_type="duplicate",
                source=duplicate_group[0],
                details={
                    "duplicates": duplicate_group,
                    "action": rule.action,
                },
            )
            self.operations.append(operation)

    def execute(self) -> List[OperationResult]:
        """Execute planned operations."""
        if self.dry_run:
            logging.info("Dry run mode - no operations will be executed")
            return []

        self.results = []

        for operation in self.operations:
            try:
                if operation.operation_type == "move":
                    self._execute_move(operation)
                elif operation.operation_type == "rename":
                    self._execute_rename(operation)
                elif operation.operation_type == "tag":
                    self._execute_tag(operation)
                elif operation.operation_type == "duplicate":
                    self._execute_duplicate(operation)

                operation.executed = True
                operation.success = True
                logging.info(f"Success: {operation}")

            except Exception as e:
                operation.executed = True
                operation.success = False
                operation.error = str(e)
                logging.error(f"Failed: {operation} - {e}")

            self.results.append(OperationResult(operation))

        return self.results

    def _execute_move(self, operation: Operation) -> None:
        """Execute move operation."""
        dest = Path(operation.details["destination"])
        if operation.details.get("create_if_missing"):
            dest.mkdir(parents=True, exist_ok=True)

        self.mover.move(operation.source, dest)

        # Apply tag if specified
        if operation.details.get("tag"):
            self.tagger.add_tag(operation.source, **operation.details["tag"])

    def _execute_rename(self, operation: Operation) -> None:
        """Execute rename operation."""
        self.renamer.rename(
            operation.source,
            replace=operation.details.get("replace"),
            prefix=operation.details.get("prefix"),
            suffix=operation.details.get("suffix"),
            separator=operation.details.get("separator", "-"),
        )

    def _execute_tag(self, operation: Operation) -> None:
        """Execute tag operation."""
        self.tagger.add_tag(operation.source, **operation.details)

    def _execute_duplicate(self, operation: Operation) -> None:
        """Execute duplicate handling operation."""
        action = operation.details.get("action", {})
        duplicates = operation.details.get("duplicates", [])

        self.deduplicator.handle_duplicates(
            duplicates,
            keep=action.get("keep", "newest"),
            tag_duplicates=action.get("tag_duplicates", False),
            duplicate_label=action.get("duplicate_label", "重复"),
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of operations."""
        return {
            "total": len(self.operations),
            "by_type": {
                "move": sum(1 for o in self.operations if o.operation_type == "move"),
                "rename": sum(1 for o in self.operations if o.operation_type == "rename"),
                "tag": sum(1 for o in self.operations if o.operation_type == "tag"),
                "duplicate": sum(1 for o in self.operations if o.operation_type == "duplicate"),
            },
            "dry_run": self.dry_run,
        }
