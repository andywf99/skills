# -*- coding: utf-8 -*-
"""
Batch PRD Preview - 批量 Word 文件转换工具
批量处理 Word 文件，转换为 Markdown 预览格式，生成汇总报告

Usage:
    python batch_preview.py --input-dir ./prds --output-dir ./output
    batch_preview.bat --input-dir ./prds --output-dir ./output
"""

import os
import sys
import argparse
import time
import re
from pathlib import Path
from datetime import datetime

# 导入转换器
sys.path.insert(0, str(Path(__file__).parent))
from word2md_cli import EnhancedWordToMarkdownConverter


def scan_word_files(input_dir: str, pattern: str = "*.docx") -> list:
    """扫描目录中的 Word 文件"""
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")

    # 同时支持 .docx 和 .doc
    patterns = [pattern]
    if pattern == "*.docx":
        patterns.append("*.doc")

    files = []
    for p in patterns:
        files.extend(input_path.glob(p))

    # 只取顶层目录的文件
    files = [f for f in files if f.parent == input_path]
    return sorted(files)


def extract_sections(content: str, max_level: int = 3) -> list:
    """从 Markdown 内容中提取章节结构"""
    sections = []
    for line in content.split("\n"):
        match = re.match(r"^#{1,6}\s+(.+)$", line)
        if match:
            level = len(line) - len(line.lstrip("#"))
            if level <= max_level:
                sections.append((level, match.group(1).strip()))
    return sections


def format_tree(sections: list) -> str:
    """格式化章节树形结构"""
    lines = []
    for level, title in sections:
        indent = "    " * (level - 1)
        prefix = "- " if level == 1 else "  - "
        lines.append(f"{indent}{prefix}{title}")
    return "\n".join(lines)


def convert_file(converter, input_file: Path, output_dir: Path):
    """转换单个文件"""
    # 创建输出子目录
    out_subdir = output_dir / input_file.stem
    out_subdir.mkdir(exist_ok=True, parents=True)

    # 输出文件路径
    out_md = out_subdir / "preview.md"

    start = time.time()
    try:
        content, messages = converter.convert(
            str(input_file), str(out_md), use_pandoc=True
        )
        elapsed = time.time() - start
        return content, elapsed, messages, True
    except Exception as e:
        elapsed = time.time() - start
        return "", elapsed, [str(e)], False


def generate_report(results: list, input_dir: str, output_dir: str, total_time: float) -> str:
    """生成汇总报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    success_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - success_count

    lines = [
        "# PRD 预览汇总报告",
        "",
        "## 处理概览",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 输入目录 | {input_dir} |",
        f"| 输出目录 | {output_dir} |",
        f"| 处理时间 | {timestamp} |",
        f"| 总文件数 | {len(results)} |",
        f"| 成功转换 | {success_count} |",
        f"| 失败数量 | {fail_count} |",
        f"| 总耗时 | {total_time:.2f}秒 |",
        "",
        "---",
        "",
        "## 章节目录概览",
        ""
    ]

    # 每个文档的章节结构
    for r in results:
        lines.append(f"### {r['name']}")
        lines.append("")
        if r["ok"] and r["sections"]:
            lines.append(format_tree(r["sections"]))
            lines.append("")
        elif not r["ok"]:
            lines.append(f"**转换失败**: {r['err']}")
            lines.append("")

        status = "✅ 成功" if r["ok"] else "❌ 失败"
        lines.append("| 状态 | 耗时 |")
        lines.append("|---|---|")
        lines.append(f"| {status} | {r['time']:.2f}秒 |")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 错误汇总
    if fail_count > 0:
        lines.append("## 错误日志")
        lines.append("")
        lines.append("| 文件名 | 错误信息 |")
        lines.append("|---|---|")
        for r in results:
            if not r["ok"]:
                lines.append(f"| {r['name']} | {r['err']} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"生成工具: batch-prd-preview")
    lines.append(f"生成时间: {timestamp}")

    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="批量 Word 文件预览转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python batch_preview.py --input-dir ./prds --output-dir ./output
  batch_preview.bat --input-dir D:/prds --output-dir D:/preview
  batch_preview.bat  # 使用默认路径
        """
    )

    parser.add_argument(
        "--input-dir",
        default="./",
        help="输入目录路径（包含 Word 文件）"
    )

    parser.add_argument(
        "--output-dir",
        default="./prd-preview-output",
        help="输出目录路径"
    )

    parser.add_argument(
        "--file-pattern",
        default="*.docx",
        help="文件匹配模式（默认 *.docx）"
    )

    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    print("=" * 60)
    print("Batch PRD Preview - 批量 Word 预览转换")
    print("=" * 60)
    print()
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()

    # 扫描文件
    try:
        files = scan_word_files(input_dir, args.file_pattern)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)

    if not files:
        print("未找到 Word 文件")
        sys.exit(0)

    print(f"找到 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f.name}")
    print()

    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True, parents=True)

    # 初始化转换器
    converter = EnhancedWordToMarkdownConverter()

    # 执行转换
    results = []
    total_start = time.time()

    print("开始转换...")
    print("-" * 40)

    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f.name}")

        content, elapsed, messages, ok = convert_file(converter, f, Path(output_dir))

        sections = extract_sections(content) if ok else []
        err = messages[-1] if not ok and messages else ""

        results.append({
            "name": f.name,
            "ok": ok,
            "time": elapsed,
            "sections": sections,
            "err": err
        })

        status = "✅ OK" if ok else "❌ FAIL"
        print(f"  {status} ({elapsed:.2f}s)")

    total_time = time.time() - total_start

    print("-" * 40)
    print(f"完成! 总耗时: {total_time:.2f}秒")
    print()

    # 生成报告
    summary = generate_report(results, input_dir, output_dir, total_time)
    summary_path = Path(output_dir) / "preview-summary.md"

    with open(summary_path, "w", encoding="utf-8") as fp:
        fp.write(summary)

    print(f"汇总报告: {summary_path}")
    print()

    # 统计输出
    success_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - success_count

    print("=" * 60)
    print("处理统计")
    print("=" * 60)
    print(f"  总文件数: {len(results)}")
    print(f"  成功转换: {success_count}")
    print(f"  失败数量: {fail_count}")
    print(f"  总耗时: {total_time:.2f}秒")
    print()

    # 返回码
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()