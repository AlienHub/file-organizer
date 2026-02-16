# File Organizer

帮助你整理文件系统，基于 YAML 规则自动化执行操作。

## 功能

- **文件移动**：按类型/来源/模式移动文件到指定目录
- **文件重命名**：去除乱码、统一格式、规范化命名
- **Mac 标签**：给文件打上颜色标签和自定义文字标签
- **重复检测**：按内容/名称检测重复文件，按规则处理
- **AI Insights**：分析目录，智能推荐整理规则

## 快速开始

### 环境要求

- macOS
- `tag` 命令行工具

```bash
brew install tag
```

### 基本使用

#### 整理下载目录

```
"帮我整理下载目录"
→ 扫描 ~/Downloads
→ 应用规则，显示预览
→ 你说"执行" → 执行操作
```

#### 给文件打标签

```bash
# 红色"待删除"标签
tag --add "待删除"$'\n'"6" file.pdf

# 蓝色"发票"标签
tag --add "发票"$'\n'"4" invoice.pdf
```

## 配置文件

位置：`~/.file-organizer/config.yaml`

```yaml
# 预览模式 (true=预览, false=执行)
dry_run: true

# 扫描目录
scan_paths:
  - ~/Downloads
  - ~/Documents
  - ~/Desktop

# 日志级别
log_level: info
```

## 规则语法

### move.yaml - 移动规则

```yaml
rules:
  - name: "微信 PDF 整理"
    condition:
      path: "~/Downloads"
      extension: ["pdf", "doc", "docx"]
      pattern: "WeChat|微信"
    action:
      move: "~/Documents/WeChat"
      create_if_missing: true
      tag:
        color: "blue"
        label: "微信"
```

### tag.yaml - 标签规则

```yaml
rules:
  - name: "大文件标签"
    condition:
      size_gt: 100MB
    action:
      tag:
        color: "red"
        label: "大文件"
```

### duplicate.yaml - 重复检测规则

```yaml
rules:
  - name: "重复处理"
    check_by: "content"
    action:
      keep: "newest"
      tag_duplicates: true
      duplicate_label: "重复"
```

## 标签颜色

| 颜色代码 | 颜色 |
|---------|------|
| 1 | 灰 |
| 2 | 绿 |
| 3 | 紫 |
| 4 | 蓝 |
| 5 | 黄 |
| 6 | 红 |
| 7 | 橙 |

## 触发方式

### 自动触发

- "整理下载目录"
- "整理桌面"
- "移动文件"
- "清理重复文件"
- "给文件打标签"
- "分析一下我的下载目录"

### 手动调用

```
/file-organizer
```

## 更多用法

详见 [SKILL.md](./SKILL.md)
