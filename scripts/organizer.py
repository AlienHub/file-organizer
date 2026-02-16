#!/usr/bin/env python3
"""File Organizer - Main entry point."""
import sys
import os
import argparse
from pathlib import Path

from config import get_config
from runner import Runner


def check_environment() -> bool:
    """Check if required environment is available."""
    import platform
    import shutil

    all_ok = True

    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Error: Python 3.8+ is required")
        all_ok = False
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check pyyaml dependency
    try:
        import yaml
        print("✓ pyyaml installed")
    except ImportError:
        print("✗ Error: pyyaml not installed")
        print("  Run: pip install pyyaml")
        all_ok = False

    # Check platform
    if platform.system() != "Darwin":
        print("⚠ Warning: Some features require macOS")

    # Check tag command (optional, only for tag features)
    if platform.system() == "Darwin":
        if shutil.which("tag"):
            print("✓ tag command available")
        else:
            print("⚠ tag command not found (optional, for tag features)")
            print("  Run: brew install tag")

    if not all_ok:
        print("\nPlease install missing dependencies before continuing.")

    return all_ok


def check_rules_status(config) -> bool:
    """检查是否有有效规则。"""
    from parser import RuleParser
    parser = RuleParser(config.rules_dir)
    rules = parser.load_all_rules()
    return any(len(rules[rule_type]) > 0 for rule_type in rules)


def init_config_from_skill():
    """从技能目录初始化配置到用户目录。"""
    import shutil

    skill_dir = Path(__file__).parent.parent / ".file-organizer"
    user_dir = Path.home() / ".file-organizer"

    if not skill_dir.exists():
        return False

    # 创建目录
    (user_dir / "rules").mkdir(parents=True, exist_ok=True)
    (user_dir / "logs").mkdir(parents=True, exist_ok=True)

    # 复制配置文件
    config_src = skill_dir / "config.yaml"
    config_dst = user_dir / "config.yaml"
    if config_src.exists() and not config_dst.exists():
        shutil.copy(config_src, config_dst)

    # 复制规则文件（只复制示例，不覆盖已存在的）
    rules_src = skill_dir / "rules"
    rules_dst = user_dir / "rules"
    if rules_src.exists():
        for rule_file in rules_src.glob("*.yaml"):
            rule_dst = rules_dst / rule_file.name
            if not rule_dst.exists():
                shutil.copy(rule_file, rule_dst)

    return True


def show_guide():
    """显示使用引导。"""
    guide = """
=== File Organizer 使用引导 ===

看起来你是第一次使用，我来帮你设置！

📁 配置目录: ~/.file-organizer/
   - rules/     规则文件
   - logs/      操作日志
   - config.yaml 配置文件

📋 可用命令:
   file-organizer --help              查看帮助
   file-organizer --scan-path ~/Downloads  扫描指定目录
   file-organizer --execute           执行操作

📝 下一步:
   1. 告诉我你想整理哪个目录
   2. 我会分析目录内容
   3. 给你建议整理规则
   4. 你确认后执行

试试说:
   "帮我整理下载目录"
   "分析一下我的桌面"
"""
    print(guide)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="File Organizer - 整理文件、移动文件、清理下载目录"
    )
    parser.add_argument(
        "--execute",
        "-e",
        action="store_true",
        help="Execute operations (default is preview mode)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        help="Custom config directory",
    )
    parser.add_argument(
        "--scan-path",
        type=str,
        help="Specific path to scan",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize config from skill directory",
    )
    parser.add_argument(
        "--insights",
        type=str,
        help="Analyze directory and show insights",
    )

    args = parser.parse_args()

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Initialize if requested
    if args.init:
        if init_config_from_skill():
            print("✓ 配置已初始化到 ~/.file-organizer/")
            print("  运行 'file-organizer --scan-path ~/Downloads' 开始整理")
        else:
            print("✗ 初始化失败")
        sys.exit(0)

    # Insights mode - 收集数据后由 AI 分析
    if args.insights:
        from utils.insights import scan_directory_basic, generate_analysis_prompt, format_insights_for_user
        data = scan_directory_basic(args.insights)
        if "error" in data:
            print(f"错误: {data['error']}")
            sys.exit(1)

        # 输出目录信息供 AI 分析
        prompt = generate_analysis_prompt(args.insights, data)
        print(prompt)
        sys.exit(0)

    # Load config
    config = get_config(args.config_dir)

    # Check if config exists, init if not
    if not config.config_file.exists():
        print("首次使用，正在初始化配置...")
        init_config_from_skill()
        # Reload config
        config = get_config(args.config_dir)

    # Check rules status
    if not check_rules_status(config):
        print("\n" + "=" * 50)
        print("未检测到有效规则！")
        print("=" * 50)
        show_guide()
        print("\n或者使用 --insights 分析目录:")
        print("  file-organizer --insights ~/Downloads")
        print("\n或者使用 --init 从技能初始化示例规则:")
        print("  file-organizer --init")
        sys.exit(0)

    # Set dry run mode
    dry_run = not args.execute
    if args.verbose:
        print(f"Mode: {'Preview' if dry_run else 'Execute'}")

    # Initialize runner
    runner = Runner(
        rules_dir=config.rules_dir,
        logs_dir=config.logs_dir,
        dry_run=dry_run,
    )

    # Scan and plan
    if args.verbose:
        print("Scanning files...")

    operations = runner.scan_and_plan()

    # Display summary
    summary = runner.get_summary()
    print(f"\n=== 操作摘要 ===")
    print(f"总操作数: {summary['total']}")
    print(f"  移动: {summary['by_type']['move']}")
    print(f"  重命名: {summary['by_type']['rename']}")
    print(f"  标签: {summary['by_type']['tag']}")
    print(f"  重复检测: {summary['by_type']['duplicate']}")

    # Show operations
    if operations:
        print(f"\n=== 预览操作 ===")
        for i, op in enumerate(operations, 1):
            print(f"{i}. [{op.operation_type}] {op.source.name}")
            if op.operation_type == "move":
                print(f"   -> {op.details.get('destination')}")
            elif op.operation_type == "rename":
                print(f"   -> {op.details}")

    # Execute if requested
    if dry_run:
        print("\n=== 预览模式 ===")
        print("使用 --execute 参数执行操作")
    else:
        print("\n=== 执行中 ===")
        results = runner.execute()
        success = sum(1 for r in results if r.operation.success)
        print(f"完成: {success}/{len(results)} 成功")


if __name__ == "__main__":
    main()
