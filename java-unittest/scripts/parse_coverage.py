#!/usr/bin/env python3
"""运行 JaCoCo 报告并解析覆盖率，检查阈值，输出未覆盖详情。

运行 mvn test jacoco:report，解析 JaCoCo XML 报告，
对比覆盖率阈值，输出未覆盖的类、方法和行号。

用法:
    python parse_coverage.py /path/to/project --threshold 90
    python parse_coverage.py /path/to/project --threshold 90 --no-run
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def find_maven() -> str | None:
    """通过 PATH 查找 Maven 可执行文件。"""
    is_windows = sys.platform == "win32"
    for name in ("mvn.cmd", "mvn.bat", "mvn") if is_windows else ("mvn",):
        found = shutil.which(name)
        if found:
            return found
    return None


def find_jacoco_xml(project_root: Path) -> Path | None:
    """查找 JaCoCo XML 报告文件。"""
    candidates = [
        project_root / "target" / "site" / "jacoco" / "jacoco.xml",
        project_root / "target" / "site" / "jacoco-ut" / "jacoco.xml",
        project_root / "target" / "jacoco-ut" / "jacoco.xml",
    ]
    for d in (project_root / "target").glob("*/site/jacoco"):
        candidates.append(d / "jacoco.xml")
    for d in (project_root / "target").glob("*/site/jacoco-ut"):
        candidates.append(d / "jacoco.xml")

    for p in candidates:
        if p.exists():
            return p
    return None


def parse_jacoco_xml(xml_path: Path) -> list[dict]:
    """解析 JaCoCo XML 报告，提取覆盖率数据。"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"解析 JaCoCo XML 失败: {e}", file=sys.stderr)
        return []

    classes = []

    for package in root.iter("package"):
        pkg_name = package.get("name", "").replace("/", ".")

        for cls in package.findall("class"):
            class_name = f"{pkg_name}.{cls.get('name', '')}"
            source_file = cls.get("sourcefilename", "")

            methods = []
            line_covered = 0
            line_missed = 0
            branch_covered = 0
            branch_missed = 0
            uncovered_lines = []
            uncovered_methods = []

            for method in cls.findall("method"):
                method_name = method.get("name", "")
                m_line_covered = 0
                m_line_missed = 0

                for counter in method.findall("counter"):
                    counter_type = counter.get("type", "")
                    covered = int(counter.get("covered", "0"))
                    missed = int(counter.get("missed", "0"))

                    if counter_type == "LINE":
                        m_line_covered = covered
                        m_line_missed = missed
                    if counter_type == "BRANCH":
                        branch_covered += covered
                        branch_missed += missed

                if m_line_missed > 0 and method_name not in ("<init>", "<clinit>", "equals", "hashCode", "toString"):
                    uncovered_methods.append(method_name)

                methods.append({
                    "name": method_name,
                    "lineCovered": m_line_covered,
                    "lineMissed": m_line_missed,
                })

            for line in cls.findall("line"):
                line_nr = int(line.get("nr", "0"))
                line_mi = int(line.get("mi", "0"))
                line_ci = int(line.get("ci", "0"))

                if line_mi > 0 and line_ci == 0:
                    uncovered_lines.append(line_nr)

                if line_ci > 0:
                    line_covered += 1
                else:
                    line_missed += 1

            for counter in cls.findall("counter"):
                counter_type = counter.get("type", "")
                covered = int(counter.get("covered", "0"))
                missed = int(counter.get("missed", "0"))
                if counter_type == "BRANCH":
                    branch_covered = covered
                    branch_missed = missed

            total_lines = line_covered + line_missed
            line_pct = (line_covered / total_lines * 100) if total_lines > 0 else 100.0

            total_branches = branch_covered + branch_missed
            branch_pct = (branch_covered / total_branches * 100) if total_branches > 0 else 100.0

            simple_class_name = class_name.split(".")[-1]
            skip_suffixes = ("DTO", "Dto", "VO", "Vo", "PO", "Po", "BO", "Bo", "Config", "Configuration",
                           "Constant", "Constants", "Enum", "Application", "Request", "Response")
            is_skip_candidate = any(simple_class_name.endswith(s) for s in skip_suffixes)

            classes.append({
                "className": class_name,
                "sourceFile": source_file,
                "lineCoverage": round(line_pct, 1),
                "branchCoverage": round(branch_pct, 1),
                "lineCovered": line_covered,
                "lineMissed": line_missed,
                "branchCovered": branch_covered,
                "branchMissed": branch_missed,
                "uncoveredMethods": uncovered_methods,
                "uncoveredLines": uncovered_lines,
                "isSkipCandidate": is_skip_candidate,
            })

    return classes


def run_maven(mvn_cmd: str, project_root: Path, goals: list[str], timeout: int = 600) -> str:
    """运行 Maven 命令并返回输出。"""
    cmd = [mvn_cmd] + goals
    print(f"执行: {' '.join(cmd)}", file=sys.stderr)

    env = os.environ.copy()

    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )

    return result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description="运行 JaCoCo 报告并解析覆盖率")
    parser.add_argument("project", type=Path, help="项目根目录路径")
    parser.add_argument("--threshold", type=float, default=90, help="覆盖率阈值（百分比，默认 90）")
    parser.add_argument("--no-run", action="store_true", help="不运行 jacoco:report，直接解析已有的 XML 报告")
    parser.add_argument("--xml-path", type=Path, default=None, help="JaCoCo XML 报告路径（默认自动查找）")
    args = parser.parse_args()

    if not args.project.is_dir():
        print(f"错误: 目录不存在: {args.project}", file=sys.stderr)
        sys.exit(2)

    # 运行 JaCoCo 报告
    if not args.no_run:
        mvn_cmd = find_maven()
        if not mvn_cmd:
            print("Maven 未找到，跳过报告生成，尝试直接查找已有报告...", file=sys.stderr)
        else:
            print(f"使用 Maven: {mvn_cmd}", file=sys.stderr)
            output = run_maven(mvn_cmd, args.project, ["test", "jacoco:report"])
            if "BUILD SUCCESS" not in output:
                output2 = run_maven(mvn_cmd, args.project, ["jacoco:report"], timeout=120)
                if "BUILD SUCCESS" not in output2:
                    print("JaCoCo 报告生成失败，尝试直接查找已有报告...", file=sys.stderr)

    # 查找 XML 报告
    xml_path = args.xml_path
    if xml_path is None:
        xml_path = find_jacoco_xml(args.project)

    if xml_path is None or not xml_path.exists():
        result = {
            "error": "未找到 JaCoCo XML 报告，请确认 jacoco-maven-plugin 已配置且报告已生成",
            "searchedPaths": [
                "target/site/jacoco/jacoco.xml",
                "target/site/jacoco-ut/jacoco.xml",
                "target/jacoco-ut/jacoco.xml",
            ],
            "threshold": args.threshold,
            "classes": [],
            "belowThreshold": [],
            "allPass": False,
        }
        print(json.dumps(result, ensure_ascii=False))
        return

    print(f"解析 JaCoCo 报告: {xml_path}", file=sys.stderr)

    # 解析 XML
    classes = parse_jacoco_xml(xml_path)

    if not classes:
        result = {
            "error": f"JaCoCo XML 报告中无类数据: {xml_path}",
            "threshold": args.threshold,
            "classes": [],
            "belowThreshold": [],
            "allPass": False,
        }
        print(json.dumps(result, ensure_ascii=False))
        return

    # 检查覆盖率阈值
    below_threshold = []
    for cls in classes:
        line_pass = cls["lineCoverage"] >= args.threshold
        branch_pass = cls["branchCoverage"] >= args.threshold or cls["branchMissed"] == 0

        cls["passLine"] = line_pass
        cls["passBranch"] = branch_pass

        if not line_pass or not branch_pass:
            gap_line = max(0, args.threshold - cls["lineCoverage"])
            gap_branch = max(0, args.threshold - cls["branchCoverage"])
            below_threshold.append({
                "className": cls["className"],
                "lineCoverage": cls["lineCoverage"],
                "branchCoverage": cls["branchCoverage"],
                "passLine": line_pass,
                "passBranch": branch_pass,
                "gapLine": round(gap_line, 1),
                "gapBranch": round(gap_branch, 1),
                "uncoveredMethods": cls["uncoveredMethods"],
                "uncoveredLines": cls["uncoveredLines"],
            })

    all_pass = len(below_threshold) == 0

    result = {
        "threshold": args.threshold,
        "reportPath": str(xml_path),
        "classes": classes,
        "belowThreshold": below_threshold,
        "allPass": all_pass,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
