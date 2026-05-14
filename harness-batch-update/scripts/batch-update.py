#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Harness 批量更新工具
支持对所有子模块执行批量操作
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class BatchUpdater:
    def __init__(self, harness_root, modules_dir='modules'):
        self.harness_root = Path(harness_root)
        self.modules_dir = self.harness_root / modules_dir

    def log(self, message, level='INFO'):
        """输出日志（不写文件）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)

    def get_modules(self):
        """获取所有子模块列表"""
        modules = []
        if not self.modules_dir.exists():
            self.log(f"Modules directory not found: {self.modules_dir}", 'ERROR')
            return modules

        for item in self.modules_dir.iterdir():
            if item.is_dir() and (item / '.git').exists():
                modules.append(item.name)

        return sorted(modules)

    def run_command(self, cmd, cwd=None, check=True):
        """执行命令"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, '', 'Command timed out'
        except Exception as e:
            return -1, '', str(e)

    def git_status(self):
        """查看所有子模块状态"""
        self.log("Checking git status for all modules...")
        modules = self.get_modules()

        results = {
            'clean': [],
            'modified': [],
            'ahead': [],
            'behind': [],
            'error': []
        }

        for module in modules:
            module_path = self.modules_dir / module
            code, stdout, stderr = self.run_command('git status --porcelain', cwd=module_path)

            if code != 0:
                results['error'].append((module, stderr))
                continue

            if stdout.strip():
                results['modified'].append((module, stdout.strip()))
            else:
                # 检查是否领先或落后远程
                code, stdout, stderr = self.run_command(
                    'git rev-list --left-right --count @{upstream}...HEAD',
                    cwd=module_path,
                    check=False
                )
                if code == 0:
                    parts = stdout.strip().split()
                    if len(parts) == 2:
                        behind, ahead = int(parts[0]), int(parts[1])
                        if ahead > 0:
                            results['ahead'].append((module, ahead))
                        elif behind > 0:
                            results['behind'].append((module, behind))
                        else:
                            results['clean'].append(module)
                else:
                    results['clean'].append(module)

        # 输出结果
        print(f"\n{'='*60}")
        print(f"Git Status Summary ({len(modules)} modules)")
        print(f"{'='*60}\n")

        if results['clean']:
            print(f"✅ Clean ({len(results['clean'])}): {', '.join(results['clean'][:10])}")
            if len(results['clean']) > 10:
                print(f"   ... and {len(results['clean']) - 10} more")

        if results['modified']:
            print(f"\n📝 Modified ({len(results['modified'])}):")
            for module, changes in results['modified']:
                print(f"   - {module}")
                for line in changes.split('\n')[:3]:
                    print(f"     {line}")

        if results['ahead']:
            print(f"\n⬆️  Ahead of remote ({len(results['ahead'])}):")
            for module, count in results['ahead']:
                print(f"   - {module} (+{count} commits)")

        if results['behind']:
            print(f"\n⬇️  Behind remote ({len(results['behind'])}):")
            for module, count in results['behind']:
                print(f"   - {module} (-{count} commits)")

        if results['error']:
            print(f"\n❌ Errors ({len(results['error'])}):")
            for module, error in results['error']:
                print(f"   - {module}: {error[:50]}")

        return results

    def git_pull(self):
        """拉取所有子模块最新代码"""
        self.log("Pulling latest changes for all modules...")
        modules = self.get_modules()

        success = []
        failed = []

        for module in modules:
            module_path = self.modules_dir / module
            self.log(f"Pulling: {module}")

            code, stdout, stderr = self.run_command('git pull', cwd=module_path)

            if code == 0:
                if 'Already up to date' in stdout or 'Already up-to-date' in stdout:
                    self.log(f"  Already up to date: {module}")
                else:
                    self.log(f"  ✅ Updated: {module}")
                success.append(module)
            else:
                self.log(f"  ❌ Failed: {module} - {stderr}", 'ERROR')
                failed.append((module, stderr))

        print(f"\n{'='*60}")
        print(f"Pull Summary: {len(success)} success, {len(failed)} failed")
        print(f"{'='*60}\n")

        return success, failed

    def git_push(self):
        """推送所有子模块的本地提交"""
        self.log("Pushing local commits for all modules...")
        modules = self.get_modules()

        success = []
        failed = []
        nothing = []

        for module in modules:
            module_path = self.modules_dir / module
            self.log(f"Pushing: {module}")

            code, stdout, stderr = self.run_command('git push', cwd=module_path)

            if code == 0:
                if 'Everything up-to-date' in stdout:
                    nothing.append(module)
                else:
                    self.log(f"  ✅ Pushed: {module}")
                    success.append(module)
            else:
                self.log(f"  ❌ Failed: {module} - {stderr}", 'ERROR')
                failed.append((module, stderr))

        print(f"\n{'='*60}")
        print(f"Push Summary: {len(success)} pushed, {len(nothing)} up-to-date, {len(failed)} failed")
        print(f"{'='*60}\n")

        return success, failed, nothing

    def run_script(self, script_cmd):
        """在所有子模块中执行脚本"""
        self.log(f"Running script in all modules: {script_cmd}")
        modules = self.get_modules()

        success = []
        failed = []

        for module in modules:
            module_path = self.modules_dir / module
            self.log(f"Running in: {module}")

            code, stdout, stderr = self.run_command(script_cmd, cwd=module_path)

            if code == 0:
                self.log(f"  ✅ Success: {module}")
                success.append((module, stdout))
            else:
                self.log(f"  ❌ Failed: {module} - {stderr}", 'ERROR')
                failed.append((module, stderr))

        print(f"\n{'='*60}")
        print(f"Script Summary: {len(success)} success, {len(failed)} failed")
        print(f"{'='*60}\n")

        return success, failed

    def update_file(self, file_path, content):
        """更新所有子模块中的文件"""
        self.log(f"Updating file in all modules: {file_path}")
        modules = self.get_modules()

        success = []
        failed = []

        for module in modules:
            module_path = self.modules_dir / module
            target_file = module_path / file_path

            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.log(f"  ✅ Updated: {module}/{file_path}")
                success.append(module)
            except Exception as e:
                self.log(f"  ❌ Failed: {module} - {str(e)}", 'ERROR')
                failed.append((module, str(e)))

        print(f"\n{'='*60}")
        print(f"File Update Summary: {len(success)} success, {len(failed)} failed")
        print(f"{'='*60}\n")

        return success, failed

    def batch_commit(self, message):
        """批量提交所有子模块的改动"""
        self.log(f"Batch committing with message: {message}")
        modules = self.get_modules()

        success = []
        failed = []
        nothing = []

        for module in modules:
            module_path = self.modules_dir / module

            # 检查是否有改动
            code, stdout, stderr = self.run_command('git status --porcelain', cwd=module_path)
            if code != 0 or not stdout.strip():
                nothing.append(module)
                continue

            # 添加所有改动
            self.run_command('git add -A', cwd=module_path)

            # 提交
            code, stdout, stderr = self.run_command(
                f'git commit -m "{message}"',
                cwd=module_path
            )

            if code == 0:
                self.log(f"  ✅ Committed: {module}")
                success.append(module)
            else:
                self.log(f"  ❌ Failed: {module} - {stderr}", 'ERROR')
                failed.append((module, stderr))

        print(f"\n{'='*60}")
        print(f"Commit Summary: {len(success)} committed, {len(nothing)} no changes, {len(failed)} failed")
        print(f"{'='*60}\n")

        return success, failed, nothing

def main():
    parser = argparse.ArgumentParser(description='Harness Batch Update Tool')
    parser.add_argument('operation', choices=[
        'list', 'git-status', 'git-pull', 'git-push',
        'run-script', 'update-file', 'batch-commit'
    ], help='Operation to perform')
    parser.add_argument('--script', help='Script command to run')
    parser.add_argument('--file', help='File path to update')
    parser.add_argument('--content', help='File content')
    parser.add_argument('--message', help='Commit message')

    args = parser.parse_args()

    harness_root = Path(__file__).parent.parent.parent
    updater = BatchUpdater(harness_root)

    if args.operation == 'list':
        modules = updater.get_modules()
        print(f"\nFound {len(modules)} modules:")
        for module in modules:
            print(f"  - {module}")

    elif args.operation == 'git-status':
        updater.git_status()

    elif args.operation == 'git-pull':
        updater.git_pull()

    elif args.operation == 'git-push':
        updater.git_push()

    elif args.operation == 'run-script':
        if not args.script:
            print("Error: --script is required for run-script operation")
            sys.exit(1)
        updater.run_script(args.script)

    elif args.operation == 'update-file':
        if not args.file or not args.content:
            print("Error: --file and --content are required for update-file operation")
            sys.exit(1)
        updater.update_file(args.file, args.content)

    elif args.operation == 'batch-commit':
        if not args.message:
            print("Error: --message is required for batch-commit operation")
            sys.exit(1)
        updater.batch_commit(args.message)

if __name__ == '__main__':
    main()
