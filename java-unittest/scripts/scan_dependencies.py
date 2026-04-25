#!/usr/bin/env python3
"""扫描 Java 源文件的依赖类型，输出需要加载的 ref 文件列表。

识别 Mapper/Feign/Redis/MQ/GraySwitch/static-mock 等依赖类型，
映射到对应的 ref/ref-xxx.md 参考文件。

用法:
    python scan_dependencies.py /path/to/project src/main/java/com/xxx/OrderService.java [file2.java ...]
"""

import json
import re
import sys
from pathlib import Path


# 依赖类型识别规则
DEPENDENCY_RULES = [
    {
        "type": "mapper",
        "refFile": "ref/ref-mapper.md",
        "patterns": [
            r"@Mapper",
            r"extends\s+BaseMapper",
            r"extends\s+ServiceImpl",
            r"Mapper\s+\w+;",          # 字段声明如 XxxMapper xxxMapper;
            r"Mapper\s*<",             # 泛型如 XxxMapper<Xxx>
            r"@TableName",
            r"BaseMapper<",
            r"lambdaQuery\(",
            r"lambdaUpdate\(",
            r"LambdaQueryWrapper",
            r"LambdaUpdateWrapper",
        ],
    },
    {
        "type": "feign",
        "refFile": "ref/ref-feign.md",
        "patterns": [
            r"@FeignClient",
            r"FeignClient\s+\w+;",
            r"FeignClient\s*<",
        ],
    },
    {
        "type": "redis",
        "refFile": "ref/ref-redis.md",
        "patterns": [
            r"RedisTemplate",
            r"StringRedisTemplate",
            r"@Cacheable",
            r"@CacheEvict",
            r"@CachePut",
            r"opsForValue",
            r"opsForHash",
            r"opsForList",
        ],
    },
    {
        "type": "mq",
        "refFile": "ref/ref-mq.md",
        "patterns": [
            r"RocketMQTemplate",
            r"RabbitTemplate",
            r"KafkaTemplate",
            r"@RocketMQMessageListener",
            r"@RabbitListener",
            r"rocketMqTemplate",
            r"convertAndSend",
            r"syncSend",
        ],
    },
    {
        "type": "gray-switch",
        "refFile": "ref/ref-gray-switch.md",
        "patterns": [
            r"GrayUtils\.isGray",
            r"GraySwitch\.of",
            r"GraySwitch\b",
            r"@Gray\b",
        ],
    },
    {
        "type": "static-mock",
        "refFile": "ref/ref-static-mock.md",
        "patterns": [
            r"SessionUtil\.",
            r"UserContext\.",
            r"UserUtils\.",
            r"OtherUserUtils\.",
            r"LocalDateTime\.now\(\)",
            r"UUID\.randomUUID\(\)",
            r"System\.currentTimeMillis\(\)",
            r"InetAddress\.getLocalHost\(\)",
            r"CollectionUtils\.isNotEmpty",
            r"CollectionUtils\.isEmpty",
            r"StringUtils\.isNotBlank",
            r"StringUtils\.isNotEmpty",
            r"StringUtils\.isEmpty",
            r"StringUtils\.isBlank",
            r"DateUtils\.",
            r"JsonUtils\.",
            r"BeanUtils\.",
        ],
    },
]


def scan_file(file_path: Path, project_root: Path) -> dict:
    """扫描单个 Java 文件，识别依赖类型。"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"file": str(file_path), "types": [], "refFiles": []}

    found_types = []
    found_refs = []

    for rule in DEPENDENCY_RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, content):
                if rule["type"] not in found_types:
                    found_types.append(rule["type"])
                if rule["refFile"] not in found_refs:
                    found_refs.append(rule["refFile"])
                break

    # 使用相对路径
    try:
        rel_path = file_path.relative_to(project_root)
    except ValueError:
        rel_path = str(file_path)

    return {
        "file": str(rel_path).replace("\\", "/"),
        "types": found_types,
        "refFiles": found_refs,
    }


def main():
    if len(sys.argv) < 3:
        print(
            "用法: python scan_dependencies.py /path/to/project file1.java [file2.java ...]",
            file=sys.stderr,
        )
        sys.exit(1)

    project_root = Path(sys.argv[1])
    if not project_root.is_dir():
        print(f"错误: 目录不存在: {project_root}", file=sys.stderr)
        sys.exit(2)

    # 解析文件参数（支持相对路径和绝对路径）
    file_args = sys.argv[2:]
    files = []
    for f in file_args:
        fpath = Path(f)
        if not fpath.is_absolute():
            fpath = project_root / f
        if fpath.exists():
            files.append(fpath)
        else:
            print(f"警告: 文件不存在: {fpath}", file=sys.stderr)

    if not files:
        result = {
            "dependencies": [],
            "allRefFiles": [],
            "message": "无可扫描的文件",
        }
        print(json.dumps(result, ensure_ascii=False))
        return

    # 扫描每个文件
    dependencies = []
    all_ref_files = []

    for f in files:
        dep = scan_file(f, project_root)
        dependencies.append(dep)
        for ref in dep["refFiles"]:
            if ref not in all_ref_files:
                all_ref_files.append(ref)

    result = {
        "dependencies": dependencies,
        "allRefFiles": all_ref_files,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
