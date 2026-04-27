#!/usr/bin/env python3
"""运行 Maven 测试并解析结果，分类错误，输出结构化错误报告。

运行 mvn test，解析输出中的测试摘要和失败详情，
按 ref-autofix.md 的错误分类表分类，输出修复优先级。

用法:
    python parse_test_result.py /path/to/project --tests "Class1Test,Class2Test"
    python parse_test_result.py /path/to/project --tests "Class1Test" --no-run
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# 错误分类规则（来自 ref-autofix.md）
ERROR_CATEGORIES = [
    (r"cannot find symbol", "missing_dependency", 1),
    (r"package .* does not exist", "missing_dependency", 1),
    (r"COMPILATION ERROR", "compilation_error", 1),
    (r"NoClassDefFoundError", "class_not_found", 2),
    (r"ClassNotFoundException", "class_not_found", 2),
    (r"NoSuchMethodError", "method_not_found", 3),
    (r"NoSuchFieldError", "method_not_found", 3),
    (r"NullPointerException", "mock_not_injected", 4),
    (r"AssertionError|AssertionFailedError", "assertion_mismatch", 5),
    (r"MockitoException|MockitoInitializationException", "mockito_config", 3),
    (r"SurefireRefuseException", "surefire_fork", 6),
    (r"org\.junit\.|org\.junit\.jupiter", "junit_config", 3),
]


def find_maven(project_root: Path) -> str | None:
    """查找用户系统环境中的 Maven 可执行文件。

    查找顺序：
    1. 项目目录下的 mvnw / mvnw.cmd（Maven Wrapper）
    2. shutil.which 在 PATH 中查找 mvn / mvn.cmd
    3. MAVEN_HOME / M2_HOME 环境变量下的 bin 目录
    """
    # 1. Maven Wrapper
    is_windows = sys.platform == "win32"
    if is_windows:
        wrapper = project_root / "mvnw.cmd"
    else:
        wrapper = project_root / "mvnw"
    if wrapper.exists():
        return str(wrapper)

    # 2. PATH 中查找
    for name in ("mvn.cmd", "mvn.bat", "mvn") if is_windows else ("mvn",):
        found = shutil.which(name)
        if found:
            return found

    # 3. MAVEN_HOME / M2_HOME
    for env_var in ("MAVEN_HOME", "M2_HOME"):
        home = os.environ.get(env_var)
        if home:
            home_path = Path(home)
            if is_windows:
                candidate = home_path / "bin" / "mvn.cmd"
            else:
                candidate = home_path / "bin" / "mvn"
            if candidate.exists():
                return str(candidate)

    return None


def classify_error(error_type: str, message: str, stack_trace: str) -> tuple[str, int]:
    """分类错误类型，返回 (category, priority)。"""
    combined = f"{error_type} {message} {stack_trace}"
    for pattern, category, priority in ERROR_CATEGORIES:
        if re.search(pattern, combined, re.IGNORECASE):
            return category, priority
    return "unknown", 9


def parse_maven_output(output: str) -> dict:
    """解析 Maven 测试输出。"""
    # 解析测试摘要: Tests run: X, Failures: Y, Errors: Z, Skipped: W
    summary_pattern = re.compile(
        r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
    )

    total = failures_count = errors_count = skipped = 0
    for m in summary_pattern.finditer(output):
        total = int(m.group(1))
        failures_count = int(m.group(2))
        errors_count = int(m.group(3))
        skipped = int(m.group(4))

    # 检测编译失败
    if "COMPILATION ERROR" in output:
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "compilationError": True,
            "failures": [],
            "priority": [],
            "rawOutput": output[-2000:] if len(output) > 2000 else output,
        }

    # 解析失败详情
    failures = []

    # 匹配模式: 测试类和方法名 + 异常
    # 格式1: [ERROR]   XxxTest.test_method:31 >> AssertionError
    failure_pattern1 = re.compile(
        r"\[ERROR\]\s+([\w.]+Test)\.(\w+)\s*:\d+\s*>>?\s*(\w+(?:Exception|Error)?)\s*(.*)",
        re.MULTILINE,
    )
    # 格式2: [ERROR] Tests run: ... in XxxTest (时间)
    failure_class_pattern = re.compile(
        r"\[ERROR\]\s+Tests run:\s*\d+.*in\s+([\w.]+Test)",
        re.MULTILINE,
    )

    matched_methods = set()

    for m in failure_pattern1.finditer(output):
        test_class = m.group(1)
        test_method = m.group(2)
        error_type = m.group(3)
        message = m.group(4).strip()
        key = f"{test_class}.{test_method}"
        if key in matched_methods:
            continue
        matched_methods.add(key)

        # 提取对应堆栈
        stack_start = output.find(key)
        stack_trace = ""
        if stack_start >= 0:
            stack_end = output.find("\n[", stack_start + 1)
            if stack_end == -1:
                stack_end = min(stack_start + 500, len(output))
            stack_trace = output[stack_start:stack_end]

        category, priority = classify_error(error_type, message, stack_trace)
        failures.append({
            "testClass": test_class,
            "testMethod": test_method,
            "errorType": error_type,
            "category": category,
            "priority": priority,
            "message": message,
            "stackTrace": stack_trace[:1000],
        })

    # 如果格式1没匹配到，尝试格式2（仅获取类名）
    if not failures:
        for m in failure_class_pattern.finditer(output):
            test_class = m.group(1)
            # 在输出中查找该类的异常类型
            class_section_start = output.find(f"[ERROR] Tests run:", m.start())
            class_section_end = output.find("\n[INFO]", class_section_start)
            if class_section_end == -1:
                class_section_end = len(output)
            class_section = output[class_section_start:class_section_end]

            # 查找异常类型
            exception_pattern = re.compile(r"(\w+(?:Exception|Error)):\s*(.*)")
            exc_match = exception_pattern.search(class_section)
            error_type = exc_match.group(1) if exc_match else "Unknown"
            message = exc_match.group(2).strip() if exc_match else ""

            category, priority = classify_error(error_type, message, class_section)
            failures.append({
                "testClass": test_class,
                "testMethod": "",
                "errorType": error_type,
                "category": category,
                "priority": priority,
                "message": message,
                "stackTrace": class_section[:1000],
            })

    # 按 priority 排序
    failures.sort(key=lambda x: x["priority"])

    # 生成修复优先级列表（按类去重）
    seen = set()
    priority_classes = []
    for f in failures:
        cls = f["testClass"]
        if cls not in seen:
            seen.add(cls)
            priority_classes.append(cls)

    passed = total - failures_count - errors_count - skipped

    return {
        "total": total,
        "passed": passed,
        "failed": failures_count,
        "errors": errors_count,
        "skipped": skipped,
        "compilationError": False,
        "failures": failures,
        "priority": priority_classes,
    }


def run_maven_test(mvn_cmd: str, project_root: Path, test_classes: str, clean: bool = True) -> str:
    """运行 Maven 测试并返回输出。"""
    cmd = [mvn_cmd]
    if clean:
        cmd.append("clean")
    cmd.extend(["test", f"-Dtest={test_classes}", "-pl", "."])

    print(f"执行: {' '.join(cmd)}", file=sys.stderr)

    # 继承用户完整环境变量，确保 JAVA_HOME 等生效
    env = os.environ.copy()

    result = subprocess.run(
        cmd,
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,  # 10 分钟超时
        env=env,
    )

    return result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description="运行 Maven 测试并解析结果")
    parser.add_argument("project", type=Path, help="项目根目录路径")
    parser.add_argument("--tests", required=True, help="测试类列表，逗号分隔（如 Class1Test,Class2Test）")
    parser.add_argument("--no-run", action="store_true", help="不运行测试，从 stdin 读取 Maven 输出进行解析")
    parser.add_argument("--no-clean", action="store_true", help="运行测试时不执行 clean")
    parser.add_argument("--mvn", type=str, default=None, help="Maven 可执行文件路径（默认自动检测）")

    args = parser.parse_args()

    if not args.no_run and not args.project.is_dir():
        print(f"错误: 目录不存在: {args.project}", file=sys.stderr)
        sys.exit(2)

    # 获取 Maven 输出
    if args.no_run:
        maven_output = sys.stdin.read()
    else:
        # 查找 Maven
        mvn_cmd = args.mvn or find_maven(args.project)
        if not mvn_cmd:
            result = {
                "error": "Maven 未找到：PATH 中无 mvn，项目目录无 mvnw，且未设置 MAVEN_HOME/M2_HOME",
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "failures": [],
                "priority": [],
            }
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(0)

        print(f"使用 Maven: {mvn_cmd}", file=sys.stderr)

        maven_output = run_maven_test(
            mvn_cmd, args.project, args.tests, clean=not args.no_clean
        )

    # 解析结果
    result = parse_maven_output(maven_output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
