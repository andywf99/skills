#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import textwrap
import xml.etree.ElementTree as et
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

MAVEN_NS = {"m": "http://maven.apache.org/POM/4.0.0"}

DEPENDENCY_MAP = {
    "spring-cloud-starter-netflix-eureka-client": "eureka",
    "spring-cloud-starter-openfeign": "feign",
    "spring-cloud-starter-netflix-hystrix": "hystrix",
    "spring-kafka": "kafka",
    "kafka-clients": "kafka",
    "spring-cloud-stream-binder-kafka": "kafka",
    "redisson-spring-boot-starter": "redis",
    "spring-cloud-starter-stream-rabbit": "stream",
    "spring-cloud-stream": "stream",
    "xxl-job-core": "xxl-job",
    "jt-platform-graceful-starter": "graceful",
    "mysql-connector-java": "dataSource",
    "druid-spring-boot-starter": "dataSource",
    "sharding-jdbc-spring-boot-starter": "dataSource",
    "rocketmq-spring-boot-starter": "rocket",
    "yl-sqs-platform-rocketmq": "rocket",
    "spring-boot-starter-web": "web-server",
}

PATTERNS = {
    "eureka_annotation": r"@Enable(?:DiscoveryClient|EurekaClient)\b",
    "feign_annotation": r"@EnableFeignClients\b",
    "feign_pre_request": r"RequestInterceptor\b|RequestTemplate\b",
    "hystrix_annotation": r"@EnableHystrix\b",
    "apollo_annotation": r"@EnableApolloConfig\b",
    "kafka_consumer": r"@KafkaListener\b|KafkaMessageListenerContainer\b|ConcurrentKafkaListenerContainerFactory\b|ConsumerFactory\b",
    "kafka_producer": r"KafkaTemplate\b|KafkaProducer\b|ProducerFactory\b",
    "stream_consumer": r"@StreamListener\b",
    "stream_binding": r"@EnableBinding\b",
    "stream_producer": r"MessageChannel\b|MessageBuilder\b|outputInterface\.[A-Za-z0-9_]+\(",
    "rocket_consumer_standard": r"@RocketMQMessageListener\b|DefaultMQPushConsumer\b|RocketMQListener\b",
    "rocket_consumer_dynamic": r"@RocketMQDynamicListener\b",
    "rocket_producer": r"RocketMQTemplate\b|RocketMQDynamicPublisher\b|syncSend\b|asyncSend\b",
    "xxl_job": r"@XxlJob\b",
    "thread_pool": r"ForkJoinPool\b|ThreadPoolExecutor\b|ThreadPoolTaskExecutor\b",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_files(root: Path, relative: str, suffix: str) -> List[Tuple[Path, str]]:
    target = root / relative
    if not target.exists():
        return []
    return [(path, read_text(path)) for path in target.rglob(f"*{suffix}")]


def parse_dependencies(pom_path: Path) -> List[Tuple[str, str, str]]:
    if not pom_path.exists():
        return []
    root = et.parse(str(pom_path)).getroot()
    dependencies: List[Tuple[str, str, str]] = []
    for dependency in root.findall(".//m:dependency", MAVEN_NS):
        group_id = dependency.findtext("m:groupId", default="", namespaces=MAVEN_NS).strip()
        artifact_id = dependency.findtext("m:artifactId", default="", namespaces=MAVEN_NS).strip()
        version = dependency.findtext("m:version", default="", namespaces=MAVEN_NS).strip()
        if artifact_id:
            dependencies.append((group_id, artifact_id, version))
    return dependencies


def find_paths(files: Sequence[Tuple[Path, str]], pattern: str) -> List[Path]:
    regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    matches: List[Path] = []
    for path, content in files:
        if regex.search(content):
            matches.append(path)
    return matches


def count_matches(files: Sequence[Tuple[Path, str]], pattern: str) -> int:
    regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    return sum(len(regex.findall(content)) for _, content in files)


def parse_apollo_namespaces(java_files: Sequence[Tuple[Path, str]]) -> List[str]:
    namespace_pattern = re.compile(r'@EnableApolloConfig\s*\(\s*value\s*=\s*\{(?P<values>.*?)\}', re.DOTALL)
    for _, content in java_files:
        match = namespace_pattern.search(content)
        if match:
            return re.findall(r'"([^"]+)"', match.group("values"))
    return []


def parse_thread_pool_beans(java_files: Sequence[Tuple[Path, str]]) -> List[str]:
    bean_pattern = re.compile(r'@Bean\s*\(\s*"([^"]+)"\s*\)')
    pools: List[str] = []
    for path, content in java_files:
        if "ThreadPool" not in path.name and "Executor" not in content and "ForkJoinPool" not in content:
            continue
        pools.extend(bean_pattern.findall(content))
    return pools


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def join_paths(paths: Iterable[Path], root: Path) -> str:
    items = [rel(path, root) for path in paths]
    return ", ".join(items[:5]) if items else "None"


def build_properties(config: Dict[str, bool], custom_rocket_consumer: bool) -> str:
    lines = [
        "graceful.enabled=true",
        f"graceful.plugin.dataSource.enabled={str(config['dataSource']).lower()}",
        f"graceful.plugin.eureka.enabled={str(config['eureka']).lower()}",
        f"graceful.plugin.redis.enabled={str(config['redis']).lower()}",
        f"graceful.plugin.hystrix.enabled={str(config['hystrix']).lower()}",
        f"graceful.plugin.stream-consumer.enabled={str(config['stream-consumer']).lower()}",
        f"graceful.plugin.stream-producer.enabled={str(config['stream-producer']).lower()}",
        f"graceful.plugin.rocket-producer.enabled={str(config['rocket-producer']).lower()}",
        f"graceful.plugin.web-server.enabled={str(config['web-server']).lower()}",
        f"graceful.plugin.xxl-job.enabled={str(config['xxl-job']).lower()}",
        "",
        f"graceful.plugin.kafka-consumer.enabled={str(config['kafka-consumer']).lower()}",
        f"graceful.plugin.kafka-producer.enabled={str(config['kafka-producer']).lower()}",
        f"graceful.plugin.feign.enabled={str(config['feign']).lower()}",
        f"graceful.plugin.feign.pre-request.enabled={str(config['feign.pre-request']).lower()}",
        "graceful.plugin.rocket-consumer.enabled=false" if custom_rocket_consumer else f"graceful.plugin.rocket-consumer.enabled={str(config['rocket-consumer']).lower()}",
        "",
        "graceful.plugin.web-server.shutdownWaitTimeSeconds=30",
        "graceful.plugin.rocket-consumer.shutdownWaitTimeSeconds=30",
        "graceful.plugin.kafka-consumer.shutdownWaitTimeSeconds=30",
        "graceful.executor.awaitTerminationSeconds=30",
    ]
    return "\n".join(lines)


def build_report(project_root: Path) -> str:
    pom_path = project_root / "pom.xml"
    dependencies = parse_dependencies(pom_path)
    dependency_artifacts = {artifact_id for _, artifact_id, _ in dependencies}
    kafka_artifacts = {"spring-kafka", "kafka-clients", "spring-cloud-stream-binder-kafka"}
    kafka_dependency_detected = any(artifact in dependency_artifacts for artifact in kafka_artifacts)

    java_files = load_files(project_root, "src/main/java", ".java")
    resource_files = load_files(project_root, "src/main/resources", ".yml") + load_files(project_root, "src/main/resources", ".yaml") + load_files(project_root, "src/main/resources", ".properties")
    all_files = list(java_files) + list(resource_files)

    apollo_namespaces = parse_apollo_namespaces(java_files)
    thread_pool_beans = parse_thread_pool_beans(java_files)
    xxl_job_count = count_matches(java_files, PATTERNS["xxl_job"])

    detected = {
        "dataSource": any(artifact in dependency_artifacts for artifact in ["mysql-connector-java", "druid-spring-boot-starter", "sharding-jdbc-spring-boot-starter"]),
        "eureka": bool(find_paths(java_files, PATTERNS["eureka_annotation"])) or "spring-cloud-starter-netflix-eureka-client" in dependency_artifacts,
        "feign": bool(find_paths(java_files, PATTERNS["feign_annotation"])) or "spring-cloud-starter-openfeign" in dependency_artifacts,
        "feign.pre-request": bool(find_paths(java_files, PATTERNS["feign_pre_request"])),
        "hystrix": bool(find_paths(java_files, PATTERNS["hystrix_annotation"])) or "spring-cloud-starter-netflix-hystrix" in dependency_artifacts,
        "kafka-consumer": kafka_dependency_detected and bool(find_paths(java_files, PATTERNS["kafka_consumer"])),
        "kafka-producer": kafka_dependency_detected and bool(find_paths(java_files, PATTERNS["kafka_producer"])),
        "redis": "redisson-spring-boot-starter" in dependency_artifacts or bool(find_paths(all_files, r"RedisTemplate\b|RedissonClient\b|redis")),
        "stream-consumer": bool(find_paths(java_files, PATTERNS["stream_consumer"])),
        "stream-producer": bool(find_paths(java_files, PATTERNS["stream_producer"])),
        "rocket-consumer": bool(find_paths(java_files, PATTERNS["rocket_consumer_standard"])),
        "rocket-producer": bool(find_paths(java_files, PATTERNS["rocket_producer"])),
        "web-server": "spring-boot-starter-web" in dependency_artifacts,
        "xxl-job": xxl_job_count > 0 or "xxl-job-core" in dependency_artifacts,
        "graceful": "jt-platform-graceful-starter" in dependency_artifacts,
    }
    rocket_consumer_dynamic_paths = find_paths(java_files, PATTERNS["rocket_consumer_dynamic"])
    if rocket_consumer_dynamic_paths:
        detected["rocket-consumer"] = True
    if detected["feign.pre-request"]:
        detected["feign"] = True

    startup_files = find_paths(java_files, r"@SpringBootApplication\b")
    apollo_missing = bool(startup_files) and apollo_namespaces and "graceful.properties" not in apollo_namespaces

    actions: List[str] = []
    if not detected["graceful"]:
        actions.append("Add `com.yl:jt-platform-graceful-starter:1.0.0-RELEASE` to `pom.xml`.")
    if apollo_missing:
        actions.append("Add `graceful.properties` to `@EnableApolloConfig(...)` so Apollo can load the new namespace.")
    if thread_pool_beans:
        actions.append("Add explicit shutdown waiting for custom executors and define the queue backlog policy.")
    if rocket_consumer_dynamic_paths:
        actions.append("Validate whether `jt-platform-graceful-starter` can control the custom `@RocketMQDynamicListener` lifecycle before enabling `graceful.plugin.rocket-consumer.enabled=true`.")
    if detected["feign"]:
        actions.append("Validate Feign client drain, retry, and timeout behavior during graceful shutdown.")
    if detected["feign.pre-request"]:
        actions.append("Validate the `feign.pre-request` hook ordering if request interceptors are already part of the project.")
    if detected["kafka-consumer"] or detected["kafka-producer"]:
        actions.append("Validate Kafka producer flush and consumer stop order in the target environment.")

    recommended = {
        "dataSource": detected["dataSource"],
        "eureka": detected["eureka"],
        "feign": detected["feign"],
        "feign.pre-request": detected["feign.pre-request"],
        "kafka-consumer": detected["kafka-consumer"],
        "kafka-producer": detected["kafka-producer"],
        "redis": detected["redis"],
        "hystrix": detected["hystrix"],
        "stream-consumer": detected["stream-consumer"],
        "stream-producer": detected["stream-producer"],
        "rocket-consumer": detected["rocket-consumer"] and not rocket_consumer_dynamic_paths,
        "rocket-producer": detected["rocket-producer"],
        "web-server": detected["web-server"],
        "xxl-job": detected["xxl-job"],
    }
    properties_block = build_properties(recommended, custom_rocket_consumer=bool(rocket_consumer_dynamic_paths))

    dependency_lines = []
    for group_id, artifact_id, version in dependencies:
        if artifact_id in DEPENDENCY_MAP:
            version_text = version or "managed"
            dependency_lines.append(f"- `{group_id}:{artifact_id}:{version_text}`")

    middleware_rows = [
        ("Eureka", detected["eureka"], join_paths(find_paths(java_files, PATTERNS["eureka_annotation"]), project_root)),
        ("Feign", detected["feign"], join_paths(find_paths(java_files, PATTERNS["feign_annotation"]), project_root)),
        ("Feign pre-request", detected["feign.pre-request"], join_paths(find_paths(java_files, PATTERNS["feign_pre_request"]), project_root)),
        ("Hystrix", detected["hystrix"], join_paths(find_paths(java_files, PATTERNS["hystrix_annotation"]), project_root)),
        ("Kafka consumer", detected["kafka-consumer"], join_paths(find_paths(java_files, PATTERNS["kafka_consumer"]), project_root)),
        ("Kafka producer", detected["kafka-producer"], join_paths(find_paths(java_files, PATTERNS["kafka_producer"]), project_root)),
        ("Redis", detected["redis"], join_paths(find_paths(all_files, r"RedisTemplate\b|RedissonClient\b|redis"), project_root)),
        ("Stream consumer", detected["stream-consumer"], join_paths(find_paths(java_files, PATTERNS["stream_consumer"]), project_root)),
        ("Stream producer", detected["stream-producer"], join_paths(find_paths(java_files, PATTERNS["stream_producer"]), project_root)),
        ("RocketMQ consumer", detected["rocket-consumer"], join_paths(rocket_consumer_dynamic_paths or find_paths(java_files, PATTERNS["rocket_consumer_standard"]), project_root)),
        ("RocketMQ producer", detected["rocket-producer"], join_paths(find_paths(java_files, PATTERNS["rocket_producer"]), project_root)),
        ("XXL-Job", detected["xxl-job"], join_paths(find_paths(java_files, PATTERNS["xxl_job"]), project_root)),
        ("Custom thread pools", bool(thread_pool_beans), ", ".join(thread_pool_beans) if thread_pool_beans else "None"),
    ]

    report = [
        "# Graceful Lifecycle Scan",
        "",
        f"- Project: `{project_root.name}`",
        f"- Starter dependency detected: `{'yes' if detected['graceful'] else 'no'}`",
        f"- Apollo namespace `graceful.properties` loaded: `{'yes' if 'graceful.properties' in apollo_namespaces else 'no'}`",
        f"- XXL-Job handlers detected: `{xxl_job_count}`",
        f"- Custom executor beans detected: `{len(thread_pool_beans)}`",
        "",
        "## Key Dependencies",
        "",
        *dependency_lines,
        "",
        "## Middleware Signals",
        "",
        "| Area | Detected | Evidence |",
        "| --- | --- | --- |",
    ]
    for name, flag, evidence in middleware_rows:
        report.append(f"| {name} | {'yes' if flag else 'no'} | {evidence or 'None'} |")

    report.extend(
        [
            "",
            "## Apollo",
            "",
            f"- Startup class: `{join_paths(startup_files, project_root)}`",
            f"- Namespaces: `{', '.join(apollo_namespaces) if apollo_namespaces else 'None detected'}`",
            f"- Missing `graceful.properties`: `{'yes' if apollo_missing else 'no'}`",
            "",
            "## Recommended graceful.properties",
            "",
            "```properties",
            properties_block,
            "```",
            "",
            "## Next Actions",
            "",
        ]
    )
    if actions:
        report.extend([f"- {action}" for action in actions])
    else:
        report.append("- No blocking gaps were detected in the static scan.")

    if rocket_consumer_dynamic_paths:
        report.extend(
            [
                "",
                "## RocketMQ Note",
                "",
                "- The repo uses `@RocketMQDynamicListener`, which is a custom listener abstraction.",
                "- Keep `graceful.plugin.rocket-consumer.enabled=false` until the starter is validated against this listener type in the target environment.",
            ]
        )

    return "\n".join(report).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Spring Boot / Spring Cloud project for graceful lifecycle integration.")
    parser.add_argument("project_root", help="Path to the project root.")
    parser.add_argument("--output", help="Optional markdown output path.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}", file=sys.stderr)
        return 1

    report = build_report(project_root)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
