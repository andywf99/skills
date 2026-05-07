#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec Archive Script
归档需求文档并生成摘要，整合核心内容后删除原始文件
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class SpecArchive:
    """需求文档归档工具"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.demand_dir = self.project_root / "docs" / "demand"
        self.summaries_dir = self.project_root / "docs" / "context" / "summaries"

        # 确保summaries目录存在
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    def scan_demands(self) -> List[str]:
        """扫描所有需求目录"""
        if not self.demand_dir.exists():
            print(f"需求目录不存在: {self.demand_dir}")
            return []

        demands = []
        for item in self.demand_dir.iterdir():
            if item.is_dir():
                demands.append(item.name)

        return sorted(demands)

    def scan_documents(self, demand_name: str) -> List[str]:
        """扫描需求目录下的所有 Markdown 文档"""
        demand_path = self.demand_dir / demand_name

        if not demand_path.exists():
            return []

        # 扫描所有 .md 文件，排除 assets 等子目录
        md_files = []
        for item in demand_path.iterdir():
            if item.is_file() and item.suffix == '.md':
                md_files.append(item.name)

        return sorted(md_files)

    def check_documents(self, demand_name: str) -> Dict[str, bool]:
        """检查需求文档是否存在（兼容旧接口）"""
        demand_path = self.demand_dir / demand_name
        documents = {}

        for doc_name in self.scan_documents(demand_name):
            doc_path = demand_path / doc_name
            documents[doc_name] = doc_path.exists()

        return documents

    def read_doc_content(self, demand_path: Path, doc_name: str) -> str:
        """读取文档内容"""
        doc_path = demand_path / doc_name
        if not doc_path.exists():
            return ""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"  读取 {doc_name} 失败: {e}")
            return ""

    def extract_key_info(self, design_content: str) -> Dict:
        """从概要设计内容提取关键信息"""
        info = {
            "需求背景": "",
            "改造目标": "",
            "数据结构变更": "",
            "接口变更": "",
            "性能设计": "",
            "安全设计": ""
        }

        if not design_content:
            return info

        # 提取需求背景
        if "## 1. 需求背景" in design_content:
            start = design_content.find("## 1. 需求背景")
            end = design_content.find("## 2.", start)
            if end == -1:
                end = len(design_content)
            background = design_content[start:end].strip()
            # 提取前500字符作为摘要
            info["需求背景"] = background[:500] + "..." if len(background) > 500 else background

        # 提取改造目标
        if "改造目标" in design_content:
            lines = design_content.split('\n')
            for line in lines:
                if "改造目标" in line or "建设目标" in line:
                    info["改造目标"] = line.strip()
                    break

        # 提取数据结构变更
        if "## 3. 数据结构" in design_content:
            start = design_content.find("## 3. 数据结构")
            end = design_content.find("## 4.", start)
            if end == -1:
                end = design_content.find("## 5.", start)
            if end == -1:
                end = len(design_content)
            info["数据结构变更"] = design_content[start:end].strip()[:800] + "..."

        # 提取接口变更
        if "## 5. 接口设计" in design_content:
            start = design_content.find("## 5. 接口设计")
            end = design_content.find("## 6.", start)
            if end == -1:
                end = design_content.find("## 7.", start)
            if end == -1:
                end = len(design_content)
            info["接口变更"] = design_content[start:end].strip()[:800] + "..."

        # 提取性能设计
        if "## 6. 性能设计" in design_content:
            start = design_content.find("## 6. 性能设计")
            end = design_content.find("## 7.", start)
            if end == -1:
                end = design_content.find("## 8.", start)
            if end == -1:
                end = len(design_content)
            info["性能设计"] = design_content[start:end].strip()[:600] + "..."

        # 提取安全设计
        if "## 9. 安全设计" in design_content:
            start = design_content.find("## 9. 安全设计")
            end = design_content.find("## 10.", start)
            if end == -1:
                end = len(design_content)
            info["安全设计"] = design_content[start:end].strip()[:600] + "..."

        return info

    def _truncate(self, content: str, limit: int = 1200) -> str:
        """截断长内容，避免摘要变成全文归档"""
        content = content.strip()
        if not content:
            return ""
        return content[:limit].rstrip() + "..." if len(content) > limit else content

    def extract_sections_by_keywords(self, content: str, keywords: List[str], limit: int = 1400) -> str:
        """按标题关键词提取核心章节；提取不到时返回文档前部摘要"""
        if not content:
            return ""

        parts = []
        lines = content.splitlines()
        heading_indexes = []

        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") and any(keyword in stripped for keyword in keywords):
                heading_indexes.append(index)

        for index in heading_indexes:
            end = len(lines)
            for next_index in range(index + 1, len(lines)):
                if lines[next_index].lstrip().startswith("#"):
                    end = next_index
                    break
            section = "\n".join(lines[index:end]).strip()
            if section:
                parts.append(section)

        if parts:
            return self._truncate("\n\n".join(parts), limit)

        return self._truncate(content, min(limit, 900))

    def extract_demand_doc_summary(self, demand_content: str) -> str:
        """从需求文档提取核心需求内容"""
        if not demand_content:
            return "（无需求文档）"

        keywords = [
            "背景", "目标", "范围", "规则", "流程", "字段", "页面", "入口",
            "验收", "约束", "口径", "影响", "需求描述", "业务"
        ]
        summary = self.extract_sections_by_keywords(demand_content, keywords, limit=1600)
        return summary if summary else "（未提取到核心需求内容）"

    def extract_design_summary(self, design_content: str, key_info: Dict) -> str:
        """从概要设计提取设计核心内容"""
        if not design_content:
            return "（无概要设计文档）"

        parts = []
        for title in ["数据结构变更", "接口变更", "性能设计", "安全设计"]:
            value = key_info.get(title, "")
            if value:
                parts.append(f"### {title}\n{value}")

        extra = self.extract_sections_by_keywords(
            design_content,
            ["架构", "流程", "配置", "任务", "消息", "数据库", "表结构", "接口", "异常", "兼容", "灰度", "回滚"],
            limit=1800
        )
        if extra and extra not in "\n\n".join(parts):
            parts.append(f"### 其他设计要点\n{extra}")

        return "\n\n".join(parts) if parts else "（未提取到核心设计内容）"

    def extract_review_summary(self, review_content: str) -> str:
        """从 review.md 提取摘要"""
        if not review_content:
            return "（无 review 文档）"

        summary_parts = []

        # 提取评审结论
        if "## 7. 我的理解" in review_content or "## 7. 待确认" in review_content:
            start = review_content.find("## 7.")
            if start != -1:
                end = review_content.find("## 8.", start)
                if end == -1:
                    end = len(review_content)
                summary_parts.append(review_content[start:end].strip())

        # 提取需澄清问题
        if "## 1. 需求描述不清晰的地方" in review_content:
            start = review_content.find("## 1. 需求描述不清晰的地方")
            end = review_content.find("## 2.", start)
            if end == -1:
                end = len(review_content)
            summary_parts.append(review_content[start:end].strip())

        if summary_parts:
            return "\n\n".join(summary_parts)

        summary = self.extract_sections_by_keywords(
            review_content,
            ["结论", "确认", "待确认", "澄清", "风险", "问题", "调整", "评审"],
            limit=1400
        )
        return summary if summary else "（未提取到关键评审内容）"

    def extract_research_summary(self, research_content: str) -> str:
        """从 research.md 提取摘要"""
        if not research_content:
            return "（无 research 文档）"

        summary_parts = []

        # 提取技术方案
        if "## 技术方案" in research_content or "## 实现方案" in research_content:
            for keyword in ["## 技术方案", "## 实现方案"]:
                start = research_content.find(keyword)
                if start != -1:
                    end = research_content.find("##", start + len(keyword))
                    if end == -1:
                        end = len(research_content)
                    summary_parts.append(research_content[start:end].strip()[:800])
                    break

        # 提取关键决策
        if "## 关键决策" in research_content or "## 技术决策" in research_content:
            for keyword in ["## 关键决策", "## 技术决策"]:
                start = research_content.find(keyword)
                if start != -1:
                    end = research_content.find("##", start + len(keyword))
                    if end == -1:
                        end = len(research_content)
                    summary_parts.append(research_content[start:end].strip()[:600])
                    break

        if summary_parts:
            return "\n\n".join(summary_parts)

        summary = self.extract_sections_by_keywords(
            research_content,
            ["技术方案", "实现方案", "关键决策", "技术决策", "依赖", "风险", "兼容", "取舍", "数据来源"],
            limit=1400
        )
        return summary if summary else "（未提取到关键研究内容）"

    def extract_plan_summary(self, plan_content: str) -> str:
        """从 plan.md 提取摘要"""
        if not plan_content:
            return "（无 plan 文档）"

        summary_parts = []

        # 提取实施计划
        if "## 实施计划" in plan_content or "## 开发计划" in plan_content:
            for keyword in ["## 实施计划", "## 开发计划"]:
                start = plan_content.find(keyword)
                if start != -1:
                    end = plan_content.find("##", start + len(keyword))
                    if end == -1:
                        end = len(plan_content)
                    summary_parts.append(plan_content[start:end].strip()[:600])
                    break

        # 提取里程碑
        if "## 里程碑" in plan_content:
            start = plan_content.find("## 里程碑")
            end = plan_content.find("##", start + len("## 里程碑"))
            if end == -1:
                end = len(plan_content)
            summary_parts.append(plan_content[start:end].strip()[:400])

        if summary_parts:
            return "\n\n".join(summary_parts)

        summary = self.extract_sections_by_keywords(
            plan_content,
            ["实施", "开发", "改动", "里程碑", "发布", "验证", "测试", "回滚", "步骤", "清单"],
            limit=1400
        )
        return summary if summary else "（未提取到关键规划内容）"

    def extract_interface_changes(self, design_content: str) -> List[Dict]:
        """从概要设计提取接口变更信息"""
        interfaces = []

        if not design_content:
            return interfaces

        # 查找接口设计章节
        if "## 5. 接口设计" in design_content or "### 接口列表" in design_content:
            lines = design_content.split('\n')
            in_table = False
            headers = []

            for i, line in enumerate(lines):
                # 检测表格开始
                if '|' in line and '接口路径' in line:
                    in_table = True
                    headers = [h.strip() for h in line.split('|') if h.strip()]
                    continue

                # 检测表格分隔行
                if in_table and ('|---' in line or '|:---' in line):
                    continue

                # 解析表格数据行
                if in_table and '|' in line and not line.strip().startswith('#'):
                    cells = [c.strip() for c in line.split('|') if c.strip()]

                    # 确保至少有接口路径和方法
                    if len(cells) >= 2:
                        interface_path = cells[0]
                        method = cells[1] if len(cells) > 1 else ''
                        function = cells[2] if len(cells) > 2 else ''
                        change_type = '新增'

                        # 判断变更类型
                        if len(cells) > 3:
                            change_desc = cells[3]
                            if '无改造' in change_desc or '无变更' in change_desc:
                                # 无改造的接口不记录，跳过
                                continue
                            elif '🔴' in change_desc or '改造' in change_desc or '扩展' in change_desc or '新增' in change_desc:
                                change_type = '修改'
                            elif '删除' in change_desc:
                                change_type = '删除'

                        interfaces.append({
                            'name': f'{method} {interface_path}',
                            'type': change_type,
                            'function': function,
                            'impact': cells[3] if len(cells) > 3 else ''
                        })

                # 表格结束
                if in_table and '|' not in line:
                    in_table = False

        return interfaces[:10]  # 最多返回10个接口

    def record_to_memory(self, demand_name: str, interface_changes: List[Dict]):
        """将接口变更记录追加到 memory.md"""
        memory_dir = self.project_root / "docs" / "context" / "memory"
        memory_file = memory_dir / "memory.md"

        # 确保目录存在
        memory_dir.mkdir(parents=True, exist_ok=True)

        # 读取现有内容
        existing_content = ""
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # 生成新的记录
        today = datetime.now().strftime('%Y-%m-%d')
        new_records = []

        if interface_changes:
            for interface in interface_changes:
                record = f"""- 日期：{today}
  需求：{demand_name}
  项目：{self.project_root.name}
  变更类型：{interface.get('type', '新增')}
  接口：{interface.get('name', '未知接口')}
  接口功能：{interface.get('function', '（待补充）')}
  影响说明：{interface.get('impact', '（待补充）')}
"""
                new_records.append(record)
        else:
            # 如果没有提取到接口变更，记录归档操作
            record = f"""- 日期：{today}
  需求：{demand_name}
  项目：{self.project_root.name}
  变更类型：归档
  接口：无
  接口功能：需求文档归档
  影响说明：已将需求文档归档至 docs/summaries/{demand_name}-summary.md
"""
            new_records.append(record)

        # 追加到文件末尾（清理旧的占位符）
        if existing_content:
            # 清理"暂无记录"占位符
            existing_content = existing_content.replace('- 暂无记录\n', '')
            existing_content = existing_content.replace('- 暂无记录', '')
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(existing_content.rstrip() + "\n\n")

        with open(memory_file, 'a', encoding='utf-8') as f:
            for record in new_records:
                f.write(record + "\n")

        print(f"  📝 已记录系统影响到 memory.md")

    def generate_summary_doc(self, demand_name: str) -> str:
        """生成摘要文档内容，整合所有文档核心内容"""
        demand_path = self.demand_dir / demand_name

        # 扫描所有文档
        doc_names = self.scan_documents(demand_name)
        documents = {name: True for name in doc_names}

        # 读取各文档内容
        doc_contents = {}
        for doc_name in doc_names:
            doc_contents[doc_name] = self.read_doc_content(demand_path, doc_name)

        # 从概要设计提取关键信息
        design_content = doc_contents.get("概要设计.md", "")
        key_info = self.extract_key_info(design_content)

        # 从其他文档提取摘要
        demand_summary = self.extract_demand_doc_summary(doc_contents.get("需求文档.md", ""))
        review_summary = self.extract_review_summary(doc_contents.get("review.md", ""))
        research_summary = self.extract_research_summary(doc_contents.get("research.md", ""))
        plan_summary = self.extract_plan_summary(doc_contents.get("plan.md", ""))
        design_summary = self.extract_design_summary(design_content, key_info)

        # 计算文档完整性
        total = len(documents)
        completed = sum(1 for exists in documents.values() if exists)
        completeness = f"{completed}/{total}"

        # 生成markdown内容
        content = f"""# 需求摘要：{demand_name}

**归档时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**需求路径**：`docs/demand/{demand_name}/`

---

## 1. 文档清单

| 文档名称 | 状态 | 备注 |
|---------|------|------|
"""

        for doc_name in doc_names:
            exists = documents.get(doc_name, False)
            status = "✅ 存在" if exists else "❌ 缺失"
            content += f"| {doc_name} | {status} | - |\n"

        content += f"""
**文档完整性**：{'✅ 完整' if completed == total else '⚠️ 不完整'} ({completeness})

---

## 2. 需求概述

### 需求背景
{key_info['需求背景'] if key_info['需求背景'] else '（未提取到需求背景）'}

### 改造目标
{key_info['改造目标'] if key_info['改造目标'] else '（未提取到改造目标）'}

---

## 3. 核心内容摘要

### 数据结构变更
{key_info['数据结构变更'] if key_info['数据结构变更'] else '（未提取到数据结构变更）'}

### 接口变更
{key_info['接口变更'] if key_info['接口变更'] else '（未提取到接口变更）'}

### 性能设计
{key_info['性能设计'] if key_info['性能设计'] else '（未提取到性能设计）'}

### 安全设计
{key_info['安全设计'] if key_info['安全设计'] else '（未提取到安全设计）'}

---

## 4. 文档路径

"""

        for doc_name in doc_names:
            doc_path = f"docs/demand/{demand_name}/{doc_name}"
            content += f"- {doc_name.replace('.md', '')}：`{doc_path}`\n"

        content += f"""
---

## 5. 需求文档内容

{demand_summary}

---

## 6. Review 评审内容

{review_summary}

---

## 7. Research 深挖内容

{research_summary}

---

## 8. Plan 规划内容

{plan_summary}

---

## 9. 概要设计内容

{design_summary}
"""

        content += """
---

**归档人**：Claude
**归档状态**：✅ 已归档
"""

        return content

    def delete_source_files(self, demand_name: str) -> int:
        """删除需求目录下的整个文件夹"""
        demand_path = self.demand_dir / demand_name

        if not demand_path.exists():
            print(f"  ⚠️  目录不存在：{demand_name}/")
            return 0

        # 统计文件数量
        file_count = sum(1 for f in demand_path.rglob('*') if f.is_file())

        # 删除整个目录
        shutil.rmtree(demand_path)
        print(f"  🗑️  已删除目录：{demand_name}/（包含 {file_count} 个文件）")

        return file_count

    def archive_demand(self, demand_name: str, force: bool = False, keep: bool = False) -> bool:
        """归档单个需求

        Args:
            demand_name: 需求名称
            force: 强制覆盖已存在的摘要文件
            keep: 保留原始文件（不删除）
        """
        summary_file = self.summaries_dir / f"{demand_name}-summary.md"

        # 检查文件是否已存在
        if summary_file.exists() and not force:
            print(f"  ⚠️  文件已存在：{summary_file}")
            print(f"  使用 --force 覆盖，或 --keep 保留旧文件")
            return False

        # 生成摘要文档
        content = self.generate_summary_doc(demand_name)

        # 写入文件
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ 已生成摘要：{summary_file.name}")

        # 提取接口变更并记录到 memory.md
        demand_path = self.demand_dir / demand_name
        design_content = self.read_doc_content(demand_path, "概要设计.md")
        interface_changes = self.extract_interface_changes(design_content)
        self.record_to_memory(demand_name, interface_changes)

        # 删除原始文件（除非指定保留）
        if not keep:
            deleted = self.delete_source_files(demand_name)
            print(f"  ✅ 已清理 {deleted} 个原始文件")
        else:
            print(f"  📁 保留原始文件（--keep 模式）")

        return True

    def archive_all(self, demand_name: Optional[str] = None, force: bool = False, keep: bool = False):
        """归档所有需求或指定需求"""
        if demand_name:
            # 归档指定需求
            demand_path = self.demand_dir / demand_name
            if not demand_path.exists():
                print(f"❌ 需求不存在：{demand_name}")
                return

            print(f"\n{'='*60}")
            print(f"归档需求：{demand_name}")
            print(f"{'='*60}\n")

            self.archive_demand(demand_name, force=force, keep=keep)
        else:
            # 归档所有需求
            demands = self.scan_demands()

            if not demands:
                print("❌ 未找到任何需求")
                return

            print(f"\n{'='*60}")
            print(f"发现 {len(demands)} 个需求")
            print(f"{'='*60}\n")

            for idx, demand in enumerate(demands, 1):
                print(f"\n[{idx}/{len(demands)}] 归档需求：{demand}")
                self.archive_demand(demand, force=force, keep=keep)

            print(f"\n{'='*60}")
            print(f"归档完成！共处理 {len(demands)} 个需求")
            print(f"摘要目录：{self.summaries_dir}")
            print(f"{'='*60}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='归档需求文档并生成摘要')
    parser.add_argument('demand_name', nargs='?', default=None,
                        help='指定需求名称，不传则归档所有需求')
    parser.add_argument('--force', '-f', action='store_true',
                        help='强制覆盖已存在的摘要文件')
    parser.add_argument('--keep', '-k', action='store_true',
                        help='保留原始文件，不删除')

    args = parser.parse_args()

    # 获取项目根目录
    project_root = os.getcwd()

    # 创建归档工具
    archive = SpecArchive(project_root)

    # 执行归档
    archive.archive_all(args.demand_name, force=args.force, keep=args.keep)


if __name__ == "__main__":
    main()
