# File Organizer

Helps you organize file systems with YAML-based rules for automated operations.

## Features

- **File Moving**: Move files by type/source/pattern to designated directories
- **File Renaming**: Remove garbled characters, unify formats, standardize naming
- **Mac Tags**: Add color tags and custom text labels to files
- **Duplicate Detection**: Find duplicate files by content/name and process by rules
- **AI Insights**: Analyze directories and intelligently recommend organization rules

## Quick Start

### Requirements

- macOS
- `tag` command-line tool

```bash
brew install tag
```

### Basic Usage

#### Organize Downloads

```
"帮我整理下载目录" (Help me organize downloads)
→ Scan ~/Downloads
→ Apply rules, show preview
→ You say "执行" (execute) → Execute operations
```

#### Tag Files

```bash
# Red "To Delete" tag
tag --add "To Delete"$'\n'"6" file.pdf

# Blue "Invoice" tag
tag --add "Invoice"$'\n'"4" invoice.pdf
```

## Configuration File

Location: `~/.file-organizer/config.yaml`

```yaml
# Preview mode (true=preview, false=execute)
dry_run: true

# Scan directories
scan_paths:
  - ~/Downloads
  - ~/Documents
  - ~/Desktop

# Log level
log_level: info
```

## Rule Syntax

### move.yaml - Move Rules

```yaml
rules:
  - name: "WeChat PDF Organization"
    condition:
      path: "~/Downloads"
      extension: ["pdf", "doc", "docx"]
      pattern: "WeChat|微信"
    action:
      move: "~/Documents/WeChat"
      create_if_missing: true
      tag:
        color: "blue"
        label: "WeChat"
```

### tag.yaml - Tag Rules

```yaml
rules:
  - name: "Large file tag"
    condition:
      size_gt: 100MB
    action:
      tag:
        color: "red"
        label: "Large File"
```

### duplicate.yaml - Duplicate Detection Rules

```yaml
rules:
  - name: "Duplicate handling"
    check_by: "content"
    action:
      keep: "newest"
      tag_duplicates: true
      duplicate_label: "Duplicate"
```

## Tag Colors

| Color Code | Color |
|------------|-------|
| 1 | gray |
| 2 | green |
| 3 | purple |
| 4 | blue |
| 5 | yellow |
| 6 | red |
| 7 | orange |

## Trigger Methods

### Auto Trigger

- "整理下载目录" (organize downloads)
- "整理桌面" (organize desktop)
- "移动文件" (move files)
- "清理重复文件" (clean duplicates)
- "给文件打标签" (tag files)
- "分析一下我的下载目录" (analyze my downloads)

### Manual Invocation

```
/file-organizer
```

## More Examples

See [SKILL.md](./SKILL.md) for detailed documentation.
