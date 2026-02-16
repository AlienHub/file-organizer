# File Organizer

AI Agent Skill - 帮助整理文件、移动文件、清理下载目录、给文件打标签。

## 功能

- **文件移动**：按类型/来源/模式移动文件到指定目录
- **文件重命名**：去除乱码、统一格式、规范化命名
- **Mac 标签**：给文件打上颜色标签和自定义文字标签
- **重复检测**：按内容/名称检测重复文件，按规则处理
- **AI Insights**：分析目录，智能推荐整理规则

## 安装

### 方式一：手动安装

1. 克隆仓库到 Skills 目录：

```bash
git clone https://github.com/AlienHub/file-organizer.git ~/.claude/skills/file-organizer
```

2. 确保已安装 `tag` 命令（macOS）：

```bash
brew install tag
```

### 方式二：发布到 Skill Market

（待完善）

## 使用

### 触发方式

直接告诉 Claude：

```
"帮我整理下载目录"
"清理桌面的旧文件"
"给这些文件打上标签"
"检查下载目录的重复文件"
"移动微信的 PDF 到 Documents"
```

### 手动调用

```
/file-organizer
```

### 示例

#### 整理下载目录

```
"帮我整理下载目录"
→ 扫描 ~/Downloads
→ 应用规则，显示预览
→ 你说"执行" → 执行操作
```

#### 给文件打标签

```
"把下载目录的旧文件标记为待删除"
→ 扫描超过180天的文件
→ 打上紫色"旧文件"标签
```

#### 清理重复文件

```
"检查下载目录的重复文件"
→ 按内容/名称检测
→ 显示重复文件列表
→ 你选择保留哪个
```

## 标签颜色

| 颜色 | 代码 | 用途 |
|------|------|------|
| 灰色 | 1 | 一般标记 |
| 绿色 | 2 | 保留/重要 |
| 紫色 | 3 | 旧文件 |
| 蓝色 | 4 | 工作相关 |
| 黄色 | 5 | 警告 |
| 红色 | 6 | 待删除 |
| 橙色 | 7 | 稍后处理 |

## 配置文件

可选：创建 `~/.file-organizer/config.yaml` 自定义配置：

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

## 规则文件

可选：创建 YAML 规则自动执行：

- `~/.file-organizer/rules/move.yaml` - 移动规则
- `~/.file-organizer/rules/tag.yaml` - 标签规则
- `~/.file-organizer/rules/rename.yaml` - 重命名规则
- `~/.file-organizer/rules/duplicate.yaml` - 重复检测规则

详见 [SKILL.md](./SKILL.md)

## 环境

- macOS
- Claude Code CLI

## License

MIT
