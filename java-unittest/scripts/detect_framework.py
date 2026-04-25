#!/usr/bin/env python3
"""检测 Java 项目的 JUnit 版本、Mock 框架和 JaCoCo 集成状态。

解析 pom.xml，检测 JUnit 版本、mockito-inline、PowerMock、JaCoCo，
应用 SKILL.md 决策表输出 mockStrategy，同时写入缓存文件。

用法:
    python detect_framework.py /path/to/project
"""

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Maven POM 命名空间
NS = {"mvn": "http://maven.apache.org/POM/4.0.0"}

# 缓存有效期（天）
CACHE_TTL_DAYS = 7


def find_pom_files(project_root: Path) -> list[Path]:
    """查找项目根目录及子模块的 pom.xml 文件。"""
    poms = []
    root_pom = project_root / "pom.xml"
    if root_pom.exists():
        poms.append(root_pom)
    # 查找子模块 pom.xml（一层深度）
    for d in project_root.iterdir():
        if d.is_dir() and (d / "pom.xml").exists():
            poms.append(d / "pom.xml")
    return poms


def parse_pom_dependencies(pom_path: Path) -> dict:
    """解析单个 pom.xml 的依赖信息。"""
    result = {
        "junit_jupiter": False,
        "mockito_inline": False,
        "powermock": False,
        "jacoco": False,
    }
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
    except ET.ParseError:
        return result

    # 检测 dependencies 中的 artifactId
    for dep in root.findall(".//mvn:dependency/mvn:artifactId", NS):
        aid = (dep.text or "").strip()
        if aid == "junit-jupiter" or aid == "junit-jupiter-api":
            result["junit_jupiter"] = True
        if aid == "mockito-inline":
            result["mockito_inline"] = True
        if aid in ("powermock-api-mockito2", "powermock-module-junit4"):
            result["powermock"] = True

    # 检测 plugins 中的 jacoco
    for plugin_aid in root.findall(".//mvn:plugin/mvn:artifactId", NS):
        aid = (plugin_aid.text or "").strip()
        if aid == "jacoco-maven-plugin":
            result["jacoco"] = True

    # 无命名空间的兜底解析（部分 pom 不使用命名空间）
    for dep in root.findall(".//dependency/artifactId"):
        aid = (dep.text or "").strip()
        if aid == "junit-jupiter" or aid == "junit-jupiter-api":
            result["junit_jupiter"] = True
        if aid == "mockito-inline":
            result["mockito_inline"] = True
        if aid in ("powermock-api-mockito2", "powermock-module-junit4"):
            result["powermock"] = True

    for plugin_aid in root.findall(".//plugin/artifactId"):
        aid = (plugin_aid.text or "").strip()
        if aid == "jacoco-maven-plugin":
            result["jacoco"] = True

    return result


def detect_framework(project_root: Path) -> dict:
    """检测框架版本并返回结果。"""
    poms = find_pom_files(project_root)
    merged = {
        "junit_jupiter": False,
        "mockito_inline": False,
        "powermock": False,
        "jacoco": False,
    }
    for pom in poms:
        deps = parse_pom_dependencies(pom)
        for k in merged:
            if deps[k]:
                merged[k] = True

    # 确定 JUnit 版本
    junit_version = "5" if merged["junit_jupiter"] else "4"

    # 应用决策表 (SKILL.md 第 44-52 行)
    if junit_version == "5":
        if merged["mockito_inline"]:
            mock_strategy = "ExtendWith_MockedStatic"
        else:
            mock_strategy = "ExtendWith_MockedStatic_NeedInline"
    else:  # JUnit 4
        if merged["mockito_inline"]:
            if merged["powermock"]:
                mock_strategy = "RunWith_MockedStatic"
            else:
                mock_strategy = "RunWith_MockedStatic"
        elif merged["powermock"]:
            mock_strategy = "RunWith_PowerMock"
        else:
            mock_strategy = "RunWith_PowerMock_NeedDeps"

    result = {
        "junitVersion": junit_version,
        "mockitoInline": merged["mockito_inline"],
        "powermock": merged["powermock"],
        "jacocoIntegrated": merged["jacoco"],
        "mockStrategy": mock_strategy,
        "detectedAt": datetime.now().isoformat(timespec="seconds"),
    }
    return result


def read_cache(project_root: Path) -> dict | None:
    """读取缓存文件，如果存在且未过期则返回内容。"""
    cache_path = project_root / ".claude" / "test-framework-cache.json"
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        detected_at = datetime.fromisoformat(cached.get("detectedAt", ""))
        delta = datetime.now() - detected_at
        if delta.days < CACHE_TTL_DAYS:
            return cached
    except (json.JSONDecodeError, ValueError, KeyError):
        pass
    return None


def write_cache(project_root: Path, data: dict) -> None:
    """写入缓存文件。"""
    cache_path = project_root / ".claude" / "test-framework-cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    if len(sys.argv) < 2:
        print("用法: python detect_framework.py /path/to/project", file=sys.stderr)
        sys.exit(1)

    project_root = Path(sys.argv[1])
    if not project_root.is_dir():
        print(f"错误: 目录不存在: {project_root}", file=sys.stderr)
        sys.exit(2)

    # 检查缓存
    cached = read_cache(project_root)
    if cached is not None:
        print(json.dumps(cached, ensure_ascii=False))
        return

    # 执行检测
    result = detect_framework(project_root)

    # 写入缓存
    write_cache(project_root, result)

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
