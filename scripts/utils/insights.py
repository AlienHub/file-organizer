"""Insights module - 使用 AI 分析目录并建议规则。

注意：这个模块只负责准备数据，实际分析由 AI/LLM 完成。
"""
import os
from pathlib import Path
from typing import Dict, List, Any


def scan_directory_basic(path: str, include_subdirs: bool = False) -> Dict[str, Any]:
    """
    快速扫描目录，返回基础统计信息供 AI 分析。

    Args:
        path: 要扫描的目录路径
        include_subdirs: 是否包含子目录

    Returns:
        {
            "total_files": int,
            "total_size": int,
            "by_extension": {"ext": count},
            "by_folder": {"folder_name": count},
            "top_files": [{"name": str, "size": int}],
            "large_files": [{"name": str, "size": int}],  # > 50MB
            "folders": [{"name": str, "count": int}]  # 子目录及文件数
        }
    """
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return {"error": f"目录不存在: {path}"}

    files = []
    folders = []
    ext_counts = {}
    folder_file_counts = {}

    for entry in os.scandir(path):
        if entry.is_file():
            try:
                stat = entry.stat()
                ext = os.path.splitext(entry.name)[1].lower().lstrip('.')

                files.append({
                    "name": entry.name,
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 1),
                    "ext": ext,
                })

                ext_counts[ext] = ext_counts.get(ext, 0) + 1
            except (OSError, PermissionError):
                continue

        elif entry.is_dir():
            # 统计子目录及其中文件数量
            subdir_count = 0
            try:
                for sub in os.scandir(entry.path):
                    if sub.is_file():
                        subdir_count += 1
            except (OSError, PermissionError):
                pass

            folders.append({
                "name": entry.name,
                "count": subdir_count,
            })
            folder_file_counts[entry.name] = subdir_count

    # 排序
    files_by_size = sorted(files, key=lambda x: x["size"], reverse=True)
    top_files = files_by_size[:20]
    large_files = [f for f in files if f["size"] > 50 * 1024 * 1024][:10]

    # 按文件数排序子目录
    folders_sorted = sorted(folders, key=lambda x: x["count"], reverse=True)

    return {
        "path": path,
        "total_files": len(files),
        "total_folders": len(folders),
        "total_size_mb": round(sum(f["size"] for f in files) / 1024 / 1024, 1),
        "by_extension": dict(sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
        "by_folder": dict(sorted(folder_file_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        "top_files": top_files,
        "large_files": large_files,
        "folders": folders_sorted,
    }


def generate_analysis_prompt(path: str, data: Dict[str, Any]) -> str:
    """
    生成 AI 分析提示词。

    Args:
        path: 要分析的目录路径
        data: scan_directory_basic 返回的基础数据

    Returns:
        完整的 prompt 字符串
    """
    ext_info = "\n".join([f"  - .{ext}: {count} 个" for ext, count in data["by_extension"].items()])

    top_files = "\n".join([
        f"  - {f['name']} ({f['size_mb']}MB)"
        for f in data["top_files"][:10]
    ])

    large_files = "\n".join([
        f"  - {f['name']} ({f['size_mb']}MB)"
        for f in data["large_files"]
    ]) if data["large_files"] else "  (无)"

    # 文件夹信息
    folder_info = ""
    if data.get("folders"):
        folder_list = "\n".join([f"  - {f['name']}: {f['count']} 个文件" for f in data["folders"][:10]])
        folder_info = f"\n### 子目录\n{folder_list}"

    prompt = f"""## 📊 目录分析任务

请分析以下目录的文件组成，并给出文件整理规则建议。

### 目录信息
- 路径: {path}
- 总文件数: {data['total_files']}
- 总文件夹数: {data.get('total_folders', 0)}
- 总大小: {data['total_size_mb']}MB

### 按扩展名统计
{ext_info}{folder_info}

### 最大文件 (TOP 10)
{top_files}

### 大文件 (>50MB)
{large_files}

---

## 💡 任务

请分析以上数据，给出：

1. **文件分类建议** - 可以按什么维度分类（类型、来源、用途等）

2. **具体规则建议** - 用 YAML 格式的 move/tag 规则，例如：
```yaml
rules:
  - name: "Excel 整理"
    condition:
      path: "~/Downloads"
      extension: ["xlsx", "xls"]
    action:
      move: "~/Documents/Excel"
      create_if_missing: true
```

3. **优先级建议** - 哪些规则最值得先执行

请直接给出规则建议，不需要解释分析过程。"""
    return prompt


def format_insights_for_user(data: Dict[str, Any], ai_suggestion: str = None) -> str:
    """
    格式化输出给用户看的分析报告。

    Args:
        data: scan_directory_basic 返回的基础数据
        ai_suggestion: AI 返回的建议（可选）

    Returns:
        格式化的报告文本
    """
    lines = []
    lines.append("=" * 50)
    lines.append("📂 目录快速扫描")
    lines.append("=" * 50)
    lines.append(f"路径: {data['path']}")
    lines.append(f"总文件数: {data['total_files']}")
    lines.append(f"总大小: {data['total_size_mb']}MB")

    if "by_extension" in data and data["by_extension"]:
        lines.append("\n📁 文件类型分布:")
        for ext, count in list(data["by_extension"].items())[:10]:
            lines.append(f"  .{ext}: {count} 个")

    if "large_files" in data and data["large_files"]:
        lines.append("\n📦 大文件 (>50MB):")
        for f in data["large_files"]:
            lines.append(f"  - {f['name']} ({f['size_mb']}MB)")

    if ai_suggestion:
        lines.append("\n" + "=" * 50)
        lines.append("💡 AI 整理建议")
        lines.append("=" * 50)
        lines.append(ai_suggestion)

    return "\n".join(lines)
