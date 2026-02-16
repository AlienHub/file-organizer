# File Organizer

AI Agent Skill - Helps organize files, move files, clean up downloads, and tag files.

## Features

- **File Moving**: Move files by type/source/pattern to designated directories
- **File Renaming**: Remove garbled characters, unify formats, standardize naming
- **Mac Tags**: Add color tags and custom text labels to files
- **Duplicate Detection**: Find duplicate files by content/name and process by rules
- **AI Insights**: Analyze directories and intelligently recommend organization rules

## Installation

### Manual Install

1. Clone the repo to your Skills directory:

```bash
git clone https://github.com/AlienHub/file-organizer.git ~/.claude/skills/file-organizer
```

2. Install `tag` command (macOS):

```bash
brew install tag
```

## Usage

### Trigger

Just tell Claude:

```
"帮我整理下载目录" (organize my downloads)
"清理桌面的旧文件" (clean old files on desktop)
"给这些文件打上标签" (tag these files)
"检查下载目录的重复文件" (check for duplicates in downloads)
```

### Manual Invocation

```
/file-organizer
```

### Examples

#### Organize Downloads

```
"帮我整理下载目录"
→ Scan ~/Downloads
→ Apply rules, show preview
→ You say "执行" → Execute
```

#### Tag Files

```
"标记下载目录超过180天的文件为旧文件"
→ Scan files older than 180 days
→ Tag with purple "旧文件" label
```

#### Clean Duplicates

```
"检查下载目录的重复文件"
→ Detect by content/name
→ Show duplicate list
→ You choose which to keep
```

## Tag Colors

| Color | Code | Usage |
|-------|------|-------|
| Gray | 1 | General |
| Green | 2 | Keep/Important |
| Purple | 3 | Old files |
| Blue | 4 | Work-related |
| Yellow | 5 | Warning |
| Red | 6 | To delete |
| Orange | 7 | Later |

## Configuration (Optional)

Create `~/.file-organizer/config.yaml`:

```yaml
# Preview mode
dry_run: true

# Directories to scan
scan_paths:
  - ~/Downloads
  - ~/Documents
  - ~/Desktop

log_level: info
```

## Rules (Optional)

Create YAML rules in `~/.file-organizer/rules/`:

- `move.yaml` - Move rules
- `tag.yaml` - Tag rules
- `rename.yaml` - Rename rules
- `duplicate.yaml` - Duplicate detection

See [SKILL.md](./SKILL.md) for details.

## Requirements

- macOS
- Claude Code CLI

## License

MIT
