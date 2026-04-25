#!/usr/bin/env python3
"""采集 Git 变更文件和变更方法。

支持三种模式：
  - diff: 对比当前分支与指定 base 分支（默认 master）
  - commit: 对比指定 commit id 之后到 HEAD 的所有变更
  - local: 对比工作区与 HEAD 的本地未提交变更

用法:
    python collect_changes.py --mode diff --base master /path/to/project
    python collect_changes.py --mode commit --base f6f19fe2 /path/to/project
    python collect_changes.py --mode local /path/to/project
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run_git(project_root: Path, args: list[str]) -> str:
    """执行 git 命令并返回 stdout。"""
    result = subprocess.run(
        ["git", "-C", str(project_root)] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(f"git 错误: {result.stderr.strip()}", file=sys.stderr)
    return result.stdout


def get_changed_files(project_root: Path, mode: str, base: str) -> list[str]:
    """获取变更文件列表，过滤非 Java 源文件和测试类。"""
    if mode == "diff":
        output = run_git(project_root, [
            "diff", "--name-only", base, "--", "src/main/java/**/*.java"
        ])
    elif mode == "commit":
        output = run_git(project_root, [
            "diff", "--name-only", f"{base}..HEAD", "--", "src/main/java/**/*.java"
        ])
    elif mode == "local":
        output = run_git(project_root, [
            "diff", "--name-only", "HEAD", "--", "src/main/java/**/*.java"
        ])
    else:
        return []

    files = [
        line.strip()
        for line in output.splitlines()
        if line.strip() and not line.strip().endswith("Test.java")
    ]
    return files


def get_untracked_files(project_root: Path) -> list[str]:
    """获取未跟踪的新 Java 源文件（仅 local 模式）。"""
    output = run_git(project_root, ["status", "--short"])
    untracked = []
    for line in output.splitlines():
        # ?? 开头表示未跟踪
        if line.startswith("??"):
            path = line[3:].strip()
            if path.startswith("src/main/java/") and path.endswith(".java") and not path.endswith("Test.java"):
                untracked.append(path)
    return untracked


def verify_commit(project_root: Path, commit_id: str) -> bool:
    """校验 commit id 是否有效。"""
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "--verify", commit_id],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def parse_method_signatures(source_content: str) -> dict[int, str]:
    """解析 Java 源文件中方法签名，建立行号→方法名映射。

    返回 {行号: 方法名} 的字典，行号为方法签名所在行。
    """
    # 匹配 Java 方法签名（排除 class/interface/enum 声明）
    pattern = re.compile(
        r"^\s*(?:public|private|protected|static|final|synchronized|abstract|native|default)*\s+"
        r"(?:[\w<>\[\],\s]+?)\s+"  # 返回类型
        r"(\w+)\s*\([^)]*\)"  # 方法名 + 参数
        r"\s*(?:throws\s+[\w\s,]+)?",
        re.MULTILINE,
    )

    method_map = {}
    lines = source_content.splitlines()
    for i, line in enumerate(lines, start=1):
        m = pattern.match(line)
        if m:
            name = m.group(1)
            # 过滤掉类名（类名通常首字母大写且与文件同名，且后面跟 { 而非 (）
            # 构造器方法名与类名相同，保留
            if name not in ("class", "interface", "enum", "new", "return", "throw", "if", "else", "switch", "for", "while", "try", "catch"):
                method_map[i] = name
    return method_map


def map_hunks_to_methods(
    diff_content: str, source_content: str
) -> list[str]:
    """将 diff hunks 映射到变更方法名。

    通过解析 @@ hunk 头获取变更行号，然后映射到源文件中的方法。
    """
    # 解析 hunk 头: @@ -old_start,old_count +new_start,new_count @@
    hunk_pattern = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", re.MULTILINE)
    method_map = parse_method_signatures(source_content)

    if not method_map:
        return []

    # 将方法行号排序
    sorted_lines = sorted(method_map.keys())
    changed_methods = set()

    for match in hunk_pattern.finditer(diff_content):
        new_start = int(match.group(1))
        # 向上查找最近的方法签名
        method_name = None
        for line_num in sorted_lines:
            if line_num <= new_start:
                method_name = method_map[line_num]
            else:
                break
        if method_name:
            changed_methods.add(method_name)

    return sorted(changed_methods)


def get_diff_content(project_root: Path, mode: str, base: str, files: list[str]) -> str:
    """获取变更文件的 diff 内容。"""
    if not files:
        return ""
    if mode == "diff":
        return run_git(project_root, ["diff", base, "--"] + files)
    elif mode == "commit":
        return run_git(project_root, ["diff", f"{base}..HEAD", "--"] + files)
    elif mode == "local":
        return run_git(project_root, ["diff", "HEAD", "--"] + files)
    return ""


def generate_diff_summary(diff_content: str, changed_methods: list[str]) -> str:
    """根据 diff 内容和变更方法生成简要描述。"""
    # 统计增删行
    added = sum(1 for line in diff_content.splitlines() if line.startswith("+") and not line.startswith("+++"))
    deleted = sum(1 for line in diff_content.splitlines() if line.startswith("-") and not line.startswith("---"))

    parts = []
    if changed_methods:
        parts.append(f"变更方法: {', '.join(changed_methods)}")
    parts.append(f"新增 {added} 行, 删除 {deleted} 行")
    return "; ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="采集 Git 变更文件和变更方法")
    parser.add_argument("project", type=Path, help="项目根目录路径")
    parser.add_argument(
        "--mode",
        choices=["diff", "commit", "local"],
        default="diff",
        help="采集模式: diff(对比分支), commit(对比commit), local(本地未提交)",
    )
    parser.add_argument("--base", default="master", help="对比基准（分支名或 commit id）")

    args = parser.parse_args()

    if not args.project.is_dir():
        print(f"错误: 目录不存在: {args.project}", file=sys.stderr)
        sys.exit(2)

    # commit 模式校验 commit id
    if args.mode == "commit":
        if not verify_commit(args.project, args.base):
            result = {
                "error": f"无效的 commit id: {args.base}",
                "mode": args.mode,
                "base": args.base,
                "files": [],
            }
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(0)

    # 获取变更文件
    changed_files = get_changed_files(args.project, args.mode, args.base)

    # local 模式额外检查未跟踪文件
    untracked = []
    if args.mode == "local":
        untracked = get_untracked_files(args.project)

    if not changed_files and not untracked:
        result = {
            "mode": args.mode,
            "base": args.base,
            "files": [],
            "untracked": [],
            "message": "无变更文件，无需生成测试",
        }
        print(json.dumps(result, ensure_ascii=False))
        return

    # 获取 diff 内容
    diff_content = get_diff_content(args.project, args.mode, args.base, changed_files)

    # 按文件分析变更方法
    file_details = []
    for f in changed_files:
        file_path = args.project / f
        if not file_path.exists():
            file_details.append({
                "path": f,
                "className": Path(f).stem,
                "changedMethods": [],
                "diffSummary": "文件已删除或不存在",
            })
            continue

        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            source = ""

        # 提取该文件的 diff 部分
        file_diff_start = diff_content.find(f"a/{f}")
        if file_diff_start == -1:
            file_diff_start = diff_content.find(f"b/{f}")
        file_diff = diff_content[file_diff_start:] if file_diff_start >= 0 else ""

        changed_methods = map_hunks_to_methods(file_diff, source)
        summary = generate_diff_summary(file_diff, changed_methods)

        file_details.append({
            "path": f,
            "className": Path(f).stem,
            "changedMethods": changed_methods,
            "diffSummary": summary,
        })

    # 未跟踪文件
    untracked_details = []
    for f in untracked:
        untracked_details.append({
            "path": f,
            "className": Path(f).stem,
            "changedMethods": [],
            "diffSummary": "新增未跟踪文件",
        })

    result = {
        "mode": args.mode,
        "base": args.base,
        "files": file_details,
        "untracked": untracked_details if untracked_details else None,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
