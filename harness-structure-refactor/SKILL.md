---
name: harness-structure-refactor
description: Use when a legacy sqs-harness submodule still has docs/architecture, docs/context, docs/demand, docs/rules, or codes/workspace and must be converted to the current arbitration-style layout.
---

# Harness Legacy Structure Migrate

## Purpose

Convert an old standalone Harness submodule into the current structure used by `modules/arbitration`.

Run this skill from the legacy module root, for example:

```powershell
cd C:\Users\pan.pan2\IdeaProjects\sqs-sub-modules\workorder
powershell -ExecutionPolicy Bypass -File C:\Users\pan.pan2\IdeaProjects\sqs-harness\skills\harness-structure-refactor\scripts\migrate-legacy-harness.ps1
```

## Source And Target

Old layout:

- `docs/architecture/`
- `docs/rules/`
- `docs/context/`
- `docs/demand/`
- `codes/workspace/`
- root `README.md`

New layout:

- `.harness/`
- `rules/`
- `docs/domain/`
- `docs/memory/demand/`
- `docs/memory/summary/`
- `docs/memory/memory.md`
- `codes/`
- `.gitkeep` in empty tracked directories

## Migration Rules

- Preserve existing business repositories by moving `codes/workspace/<repo>` to `codes/<repo>`.
- Preserve demand materials by moving `docs/demand/*` to `docs/memory/demand/`.
- Preserve summaries by moving `docs/context/summaries/*` to `docs/memory/summary/`.
- Preserve memory by moving `docs/context/memory/memory.md` to `docs/memory/memory.md`.
- Preserve code overview by moving `docs/architecture/code-overview.md` to `docs/domain/TechWhitepaper.md`.
- Preserve product whitepaper if present by moving `docs/whitepaper/ProductWhitepaper.md` to `docs/domain/ProductWhitepaper.md`.
- Move rules from `docs/rules/` or `docs/architecture/` to `rules/`.
- Move Harness docs from `docs/architecture/` to `.harness/`.
- Rewrite `AGENTS.md`, `.module-manifest.yaml`, `CLAUDE.md`, `.gitignore`, and module skill path references.
- Delete only old placeholder files and empty old directories.
- Never enter or rewrite files inside `codes/<repo>/`.

## Execution

1. Check current directory:

```powershell
Get-ChildItem -Force
```

Required files:

- `AGENTS.md`
- `.module-manifest.yaml`
- `docs/`
- `skills/`

2. Run the script:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\pan.pan2\IdeaProjects\sqs-harness\skills\harness-structure-refactor\scripts\migrate-legacy-harness.ps1
```

3. Verify:

```powershell
rg -n "docs/(architecture|rules|context|whitepaper|demand)|codes/workspace" . --glob "!codes/**" -g "*.md" -g "*.yaml" -g "*.yml"
git diff --check
git status --short
```

Expected:

- No old path matches outside `codes/**`.
- `git diff --check` exits cleanly.
- New files appear under `.harness/`, `rules/`, `docs/domain/`, and `docs/memory/`.

## Safety Notes

- The script is idempotent: running it again should not duplicate moved content.
- It does not commit or push.
- If a destination file already exists, the script keeps it and does not overwrite business content except standard navigation/rule files.
- If `codes/workspace` contains repositories, they are moved one level up; if `codes/<repo>` already exists, that repo is skipped and reported.
