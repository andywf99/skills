#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def run_git(repo: Path, args: list[str], *, check: bool = True, stdin: str | None = None):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=stdin,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed with exit code {result.returncode}: "
            f"{result.stderr.strip()}"
        )
    return result


def resolve_commit(repo: Path, commit: str) -> str:
    return run_git(repo, ["rev-parse", "--verify", f"{commit}^{{commit}}"]).stdout.strip()


def resolve_parent(repo: Path, commit: str) -> str:
    result = run_git(repo, ["rev-parse", "--verify", f"{commit}^"], check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    return EMPTY_TREE


def compress_ranges(lines: list[int]) -> str:
    unique = sorted(set(lines))
    if not unique:
        return ""

    ranges: list[str] = []
    start = prev = unique[0]
    for line in unique[1:]:
        if line == prev + 1:
            prev = line
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = line
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(ranges)


def diff_added_lines(repo: Path, base: str, target: str):
    diff = run_git(
        repo,
        ["diff", "--no-ext-diff", "--unified=0", "--no-renames", base, target, "--"],
    ).stdout

    added_by_file: dict[str, list[int]] = {}
    current_file: str | None = None
    new_line = 0
    deletions = 0

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[len("+++ b/") :]
            if current_file == "/dev/null":
                current_file = None
            elif current_file not in added_by_file:
                added_by_file[current_file] = []
            continue

        if line.startswith("@@ "):
            marker = line.split(" @@ ", 1)[0]
            plus_part = next((part for part in marker.split() if part.startswith("+")), "")
            plus_part = plus_part[1:]
            new_line = int(plus_part.split(",", 1)[0])
            continue

        if current_file is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            added_by_file[current_file].append(new_line)
            new_line += 1
            continue

        if line.startswith("-") and not line.startswith("---"):
            deletions += 1
            continue

        if line and not line.startswith("\\"):
            new_line += 1

    return added_by_file, deletions


def prompt_hash(tool: str, agent_id: str) -> str:
    return hashlib.sha256(f"{tool}:{agent_id}".encode("utf-8")).hexdigest()[:16]


def commit_author(repo: Path, commit: str) -> str:
    name = run_git(repo, ["show", "-s", "--format=%an", commit]).stdout.strip()
    email = run_git(repo, ["show", "-s", "--format=%ae", commit]).stdout.strip()
    return f"{name} <{email}>"


def build_note(
    repo: Path,
    commit: str,
    *,
    tool: str,
    model: str,
    agent_id: str,
    human_author: str,
    git_ai_version: str,
    total_additions: int | None,
    total_deletions: int | None,
    accepted_lines: int | None,
    overriden_lines: int,
):
    base = resolve_parent(repo, commit)
    added_by_file, diff_deletions = diff_added_lines(repo, base, commit)

    note_lines: list[str] = []
    attributed_lines = 0
    phash = prompt_hash(tool, agent_id)

    for file_name in sorted(added_by_file):
        lines = added_by_file[file_name]
        if not lines:
            continue
        attributed_lines += len(lines)
        rendered_file = f'"{file_name}"' if any(ch.isspace() for ch in file_name) else file_name
        note_lines.append(rendered_file)
        note_lines.append(f"  {phash} {compress_ranges(lines)}")

    if attributed_lines == 0:
        raise RuntimeError(f"commit {commit} has no added lines relative to first parent")

    effective_total_additions = total_additions if total_additions is not None else attributed_lines
    effective_total_deletions = total_deletions if total_deletions is not None else diff_deletions
    effective_accepted_lines = accepted_lines if accepted_lines is not None else attributed_lines

    metadata = {
        "schema_version": "authorship/3.0.0",
        "git_ai_version": git_ai_version,
        "base_commit_sha": commit,
        "prompts": {
            phash: {
                "agent_id": {
                    "tool": tool,
                    "id": agent_id,
                    "model": model,
                },
                "human_author": human_author,
                "total_additions": effective_total_additions,
                "total_deletions": effective_total_deletions,
                "accepted_lines": effective_accepted_lines,
                "overriden_lines": overriden_lines,
            }
        },
    }

    note_lines.append("---")
    note_lines.append(json.dumps(metadata, ensure_ascii=False, indent=2))
    return "\n".join(note_lines), phash, attributed_lines


def has_existing_note(repo: Path, commit: str) -> bool:
    result = run_git(repo, ["notes", "--ref=ai", "show", commit], check=False)
    return result.returncode == 0


def write_note(repo: Path, commit: str, note: str, *, overwrite: bool) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, newline="\n") as tmp:
        tmp.write(note)
        tmp_path = Path(tmp.name)
    try:
        args = ["notes", "--ref=ai", "add", "-F", str(tmp_path), commit]
        if overwrite:
            args = ["notes", "--ref=ai", "add", "-f", "-F", str(tmp_path), commit]
        run_git(repo, args)
    finally:
        tmp_path.unlink(missing_ok=True)


def yes(answer: str) -> bool:
    return answer.strip() in {"y", "Y", "yes", "YES"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate, preview, and optionally write a git-ai authorship note for an existing commit."
    )
    parser.add_argument("--repo", "-R", default=".", help="Worktree path or git-dir path. Default: current directory.")
    parser.add_argument("--commit", "-C", default="HEAD", help="Commit to annotate. Default: HEAD.")
    parser.add_argument("--tool", "-T", default="codex", help="AI tool name. Default: codex.")
    parser.add_argument("--model", "-M", default="manual", help="Model name. Default: manual.")
    parser.add_argument("--agent-id", "-A", default="", help="Agent id. Default: manual-<commit>.")
    parser.add_argument("--human-author", "-H", default="", help="Human author. Default: commit author.")
    parser.add_argument("--git-ai-version", default="1.3.4", help="git-ai version to put in note metadata.")
    parser.add_argument("--total-additions", type=int, default=None)
    parser.add_argument("--total-deletions", type=int, default=None)
    parser.add_argument("--accepted-lines", type=int, default=None)
    parser.add_argument("--overriden-lines", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true", help="Preview only; do not ask or write.")
    parser.add_argument("--report-json", action="store_true", help="Print a compact JSON report after preview/write.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()

    git_dir = run_git(repo, ["rev-parse", "--git-dir"]).stdout.strip()
    commit = resolve_commit(repo, args.commit)
    agent_id = args.agent_id.strip() or f"manual-{commit}"
    human_author = args.human_author.strip() or commit_author(repo, commit)
    existing = has_existing_note(repo, commit)

    print(f"Target repo: {repo}")
    print(f"Git dir: {git_dir}")
    print(f"Target commit: {commit}")

    if existing:
        print("Existing refs/notes/ai note: yes, confirmed write will overwrite it.")
    else:
        print("Existing refs/notes/ai note: no.")
        if not args.dry_run:
            answer = input("AI note is missing for this commit. Generate a repair note now? Type y to continue: ")
            if not yes(answer):
                print("Aborted; no note was generated or written.")
                return 0

    note, phash, attributed_lines = build_note(
        repo,
        commit,
        tool=args.tool,
        model=args.model,
        agent_id=agent_id,
        human_author=human_author,
        git_ai_version=args.git_ai_version,
        total_additions=args.total_additions,
        total_deletions=args.total_deletions,
        accepted_lines=args.accepted_lines,
        overriden_lines=args.overriden_lines,
    )

    print()
    print("Generated AI note preview:")
    print("------------------------------------------------------------")
    print(note)
    print("------------------------------------------------------------")

    if args.dry_run:
        print("DryRun enabled; no note was written.")
    else:
        action = "overwrite existing refs/notes/ai note" if existing else "write refs/notes/ai note"
        answer = input(f"Confirm to {action} for this commit? Type y to continue: ")
        if not yes(answer):
            print("Aborted; no note was written.")
            return 0
        write_note(repo, commit, note, overwrite=existing)
        print(f"Wrote git-ai authorship note for {commit}")
        print(f"AI attributed added lines: {attributed_lines}")
        print(f"Prompt hash: {phash}")

    if args.report_json:
        report = {
            "success": True,
            "commit": commit,
            "has_existing_note": existing,
            "prompt_hash": phash,
            "attributed_lines": attributed_lines,
            "dry_run": args.dry_run,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))

    print()
    print("Verify:")
    print(f'  git -C "{repo}" notes --ref=ai show {commit}')
    print(f'  git -C "{repo}" show --notes=ai --stat {commit}')
    print(f"  git-ai stats {commit}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
