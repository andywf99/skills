#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建新的 harness 模块子模块
支持：初始化结构 → 创建 GitLab 项目 → 推送代码 → 添加为 submodule
"""

import os
import sys
import subprocess
import yaml
import re

def run_cmd(cmd, cwd=None, check=True):
    """执行 shell 命令"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.returncode, result.stdout, result.stderr

def load_module_registry(registry_path):
    """加载模块注册表"""
    with open(registry_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_repo_info(module_name, repo_name, registry):
    """从注册表获取仓库信息"""
    for module in registry.get('modules', []):
        if module['name'] == module_name:
            for repo in module.get('repos', []):
                if repo['name'] == repo_name:
                    return repo
    return None

def create_gitlab_project(module_name, token=None, group_id=3396):
    """创建 GitLab 项目"""
    project_name = f"sqs-harness-module-{module_name}"
    url = f"http://code.jms.com/ai-coding/{project_name}.git"

    if token:
        # 使用 API 创建
        cmd = f'''curl -s --request POST "http://code.jms.com/api/v4/projects" \
            --header "PRIVATE-TOKEN: {token}" \
            --header "Content-Type: application/json" \
            --data '{{"name": "{project_name}", "namespace_id": {group_id}, "visibility": "private", "initialize_with_readme": false}}'
        '''
        run_cmd(cmd, check=False)
        print(f"✅ GitLab project created: {project_name}")
    else:
        print(f"⚠️  No GitLab token provided, skipping project creation")
        print(f"   Please create project manually: http://code.jms.com/ai-coding/{project_name}")

    return url

def update_agents_md(module_name, display_name, repos, harness_root):
    """更新 AGENTS.md 添加项目代码绑定"""
    agents_file = os.path.join(harness_root, 'modules', module_name, 'AGENTS.md')

    if not os.path.exists(agents_file):
        print(f"⚠️  AGENTS.md not found: {agents_file}")
        return

    with open(agents_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 生成项目代码绑定内容
    code_section = """
## 绑定项目代码

本模块关联以下业务代码仓库：

"""

    for idx, repo in enumerate(repos, 1):
        repo_name = repo.get('name', repo) if isinstance(repo, dict) else repo
        layer = repo.get('layer', '') if isinstance(repo, dict) else ''
        code_section += f"""| 序号 | 仓库名 | 层级 | 目录路径 |
|------|--------|------|----------|
| {idx} | `{repo_name}` | {layer} | `codes/{repo_name}` |

"""

    code_section += """### 克隆业务代码

```bash
# 进入模块目录
cd modules/""" + module_name + """

# 克隆业务代码到工作区
cd codes
"""

    for repo in repos:
        repo_name = repo.get('name', repo) if isinstance(repo, dict) else repo
        http_url = repo.get('http_url', f'http://code.jms.com/yl/{repo_name}.git') if isinstance(repo, dict) else f'http://code.jms.com/yl/{repo_name}.git'
        code_section += f"git clone {http_url} {repo_name}\n"

    code_section += """
# 返回模块根目录
cd ../..
```
"""

    # 检查是否已有"绑定项目代码"章节
    if '## 绑定项目代码' in content:
        pattern = r'## 绑定项目代码.*?(?=\n## 按任务加载|\Z)'
        content = re.sub(pattern, code_section.strip(), content, flags=re.DOTALL)
    else:
        content = content.rstrip() + '\n' + code_section

    with open(agents_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Updated AGENTS.md with {len(repos)} repos")

def main():
    harness_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    registry_path = os.path.join(harness_root, 'skills', 'harness-init-module-structure', 'assets', 'module-registry.yaml')

    # 解析参数
    if len(sys.argv) < 2:
        print("Usage: python create-module.py <module-name> [display-name] [gitlab-url] [repo1,repo2,...]")
        print("Example: python create-module.py workorder 普通工单 http://code.jms.com/ai-coding/sqs-harness-module-workorder.git yl-web-sqs-workorder,yl-jms-css-workorder-api")
        sys.exit(1)

    module_name = sys.argv[1]
    display_name = sys.argv[2] if len(sys.argv) > 2 else module_name
    gitlab_url = sys.argv[3] if len(sys.argv) > 3 else f"http://code.jms.com/ai-coding/sqs-harness-module-{module_name}.git"
    repos_str = sys.argv[4] if len(sys.argv) > 4 else ""

    print(f"\n{'='*60}")
    print(f"Creating harness module: {module_name}")
    print(f"Display name: {display_name}")
    print(f"GitLab URL: {gitlab_url}")
    print(f"{'='*60}\n")

    # Step 1: 初始化 harness 结构
    print("Step 1: Initializing harness structure...")
    target_dir = os.path.join(harness_root, 'modules', module_name)
    script_path = os.path.join(harness_root, 'skills', 'harness-init-module-structure', 'scripts', 'init-harness-module-structure.ps1')

    if os.path.exists(target_dir):
        print(f"⚠️  Directory already exists: {target_dir}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            sys.exit(0)

    run_cmd(f'powershell -ExecutionPolicy Bypass -File "{script_path}" -TargetDir "{target_dir}" -ModuleName "{module_name}"')
    print(f"✅ Harness structure initialized at: {target_dir}\n")

    # Step 2: 创建 .gitignore
    print("Step 2: Creating .gitignore...")
    gitignore_content = """# IDE
.idea/
.claude/

# 业务代码工作区
codes/*
!codes/.gitkeep
"""
    with open(os.path.join(target_dir, '.gitignore'), 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ .gitignore created\n")

    # Step 3: 创建 GitLab 项目（可选）
    print("Step 3: Creating GitLab project...")
    gitlab_token = os.environ.get('GITLAB_TOKEN', '')
    create_gitlab_project(module_name, gitlab_token)
    print()

    # Step 4: 推送到 GitLab
    print("Step 4: Pushing to GitLab...")
    run_cmd('git init', cwd=target_dir)
    run_cmd('git add -A', cwd=target_dir)
    run_cmd(f'git commit -m "init {module_name} harness module structure"', cwd=target_dir)
    run_cmd(f'git remote add origin {gitlab_url}', cwd=target_dir, check=False)
    run_cmd('git branch -M master', cwd=target_dir)
    code, stdout, stderr = run_cmd('git push -u origin master --force', cwd=target_dir, check=False)
    if code == 0:
        print(f"✅ Pushed to GitLab: {gitlab_url}\n")
    else:
        print(f"⚠️  Push failed, you may need to create the GitLab project first")
        print(f"   Error: {stderr}\n")

    # Step 5: 更新 AGENTS.md（如果提供了业务仓库）
    if repos_str:
        print("Step 5: Updating AGENTS.md with business repos...")
        registry = load_module_registry(registry_path)
        repo_names = [r.strip() for r in repos_str.split(',')]

        repos_info = []
        for repo_name in repo_names:
            repo_info = get_repo_info(module_name, repo_name, registry)
            if repo_info:
                repos_info.append(repo_info)
            else:
                repos_info.append({'name': repo_name, 'layer': '', 'http_url': f'http://code.jms.com/yl/{repo_name}.git'})

        update_agents_md(module_name, display_name, repos_info, harness_root)

        # 提交 AGENTS.md 更新
        run_cmd('git add AGENTS.md', cwd=target_dir)
        run_cmd(f'git commit -m "更新 AGENTS.md 绑定项目代码仓库信息"', cwd=target_dir)
        run_cmd('git push', cwd=target_dir)
        print()

    # Step 6: 添加为 submodule
    print("Step 6: Adding as submodule...")
    os.chdir(harness_root)

    # 检查是否已存在
    code, stdout, _ = run_cmd(f'git config -f .gitmodules --get submodule.{module_name}.path', check=False)
    if code == 0 and stdout.strip():
        print(f"⚠️  Submodule already exists: {module_name}")
    else:
        run_cmd(f'git submodule add {gitlab_url} modules/{module_name}')
        run_cmd(f'git config -f .gitmodules submodule.{module_name}.branch master')
        print(f"✅ Submodule added: {module_name}\n")

    # Step 7: 提交到父仓库
    print("Step 7: Committing to parent repository...")
    run_cmd('git add .gitmodules')
    run_cmd(f'git add modules/{module_name}')
    run_cmd(f'git commit -m "添加 {module_name} 子模块"')
    print(f"✅ Committed to parent repository\n")

    print(f"{'='*60}")
    print(f"✅ Module creation completed: {module_name}")
    print(f"{'='*60}\n")
    print(f"Next steps:")
    print(f"1. Push parent repository: git push")
    print(f"2. Clone business repos: cd modules/{module_name}/codes && git clone ...")
    print(f"3. Update docs/domain/TechWhitepaper.md after cloning repos")

if __name__ == '__main__':
    main()
