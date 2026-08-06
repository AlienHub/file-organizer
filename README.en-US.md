

# File Organizer

AI Agent Skill - Helps organize files, move files, clean up download directories, and tag files.

## Features

- **File Moving**: Move files to specified directories based on type/source/pattern
- **File Renaming**: Remove garbled text, standardize formats, and normalize naming
- **macOS Tags**: Apply color tags and custom text labels to files
- **Duplicate Detection**: Detect duplicate files by content/name and handle them according to rules
- **AI Insights**: Analyze directories and intelligently recommend organization rules

## Installation

### Method 1: Manual Installation

1. Clone the repository into the Skills directory:

```bash
git clone https://github.com/AlienHub/file-organizer.git ~/.claude/skills/file-organizer
```

2. Ensure the `tag` command is installed (macOS):

```bash
brew install tag
```

### Method 2: Publish to Skill Market

(To be completed)

## Usage

### Trigger Method

Simply tell Claude:

```
"Help me organize the Downloads folder"
"Clean up old files on the Desktop"
"Tag these files"
"Check for duplicate files in the Downloads folder"
"Move WeChat PDFs to Documents"
```

### Manual Invocation

```
/file-organizer
```

### Examples

#### Organize Downloads Folder

```
"Help me organize the Downloads folder"
→ Scans ~/Downloads
→ Applies rules and shows preview
→ You say "execute" → Executes operations
```

#### Tag Files

```
"Mark old files in the Downloads folder as pending deletion"
→ Scans files older than 180 days
→ Applies purple "Old Files" tag
```

#### Clean Up Duplicate Files

```
"Check for duplicate files in the Downloads folder"
→ Detects by content/name
→ Displays list of duplicates
→ You choose which to keep
```

## Tag Colors

| Color | Code | Usage |
|-------|------|-------|
| Gray | 1 | General marking |
| Green | 2 | Keep/Important |
| Purple | 3 | Old files |
| Blue | 4 | Work-related |
| Yellow | 5 | Warning |
| Red | 6 | To be deleted |
| Orange | 7 | Handle later |

## Configuration File

Optional: Create `~/.file-organizer/config.yaml` to customize configuration:

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

## Rule Files

Optional: Create YAML rules for automatic execution:

- `~/.file-organizer/rules/move.yaml` - Move rules
- `~/.file-organizer/rules/tag.yaml` - Tag rules
- `~/.file-organizer/rules/rename.yaml` - Rename rules
- `~/.file-organizer/rules/duplicate.yaml` - Duplicate detection rules

See [SKILL.md](./SKILL.md) for details.

## Environment

- macOS
- Claude Code CLI

## License

MIT
