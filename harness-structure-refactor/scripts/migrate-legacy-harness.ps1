param(
    [string]$ModuleRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

function Ensure-Dir {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Move-FileIfNeeded {
    param(
        [string]$From,
        [string]$To
    )
    if (Test-Path -LiteralPath $From -PathType Leaf) {
        Ensure-Dir -Path (Split-Path -Parent $To)
        if (-not (Test-Path -LiteralPath $To)) {
            Move-Item -LiteralPath $From -Destination $To -Force
            return "moved"
        }
        return "kept-target"
    }
    return "missing"
}

function Move-DirContentsIfNeeded {
    param(
        [string]$From,
        [string]$To
    )
    $moved = 0
    $skipped = 0
    if (Test-Path -LiteralPath $From -PathType Container) {
        Ensure-Dir -Path $To
        Get-ChildItem -LiteralPath $From -Force | ForEach-Object {
            $target = Join-Path $To $_.Name
            if (Test-Path -LiteralPath $target) {
                $script:SkippedItems += $target
                $skipped++
            } else {
                Move-Item -LiteralPath $_.FullName -Destination $target -Force
                $moved++
            }
        }
    }
    return @{ moved = $moved; skipped = $skipped }
}

function Remove-FileIfExists {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        Remove-Item -LiteralPath $Path -Force
    }
}

function Remove-EmptyDir {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path -PathType Container) {
        $items = Get-ChildItem -LiteralPath $Path -Force
        if ($items.Count -eq 0) {
            Remove-Item -LiteralPath $Path -Force
        }
    }
}

function Replace-InTextFile {
    param(
        [string]$Path,
        [hashtable]$Map
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return
    }
    $content = Get-Content -LiteralPath $Path -Raw
    $updated = $content
    foreach ($key in $Map.Keys) {
        $updated = $updated.Replace($key, $Map[$key])
    }
    if ($updated -ne $content) {
        Set-Content -LiteralPath $Path -Value $updated.TrimEnd() -Encoding UTF8
    }
}

function Get-Section {
    param(
        [string]$Text,
        [string]$StartHeading,
        [string]$NextHeading
    )
    $pattern = "(?s)$([regex]::Escape($StartHeading)).*?(?=\r?\n$([regex]::Escape($NextHeading))|\z)"
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) {
        return $match.Value.TrimEnd()
    }
    return $null
}

function Normalize-BindingSection {
    param(
        [string]$Section,
        [string]$ModuleName
    )
    if (-not $Section) {
        return "## 绑定项目代码`r`n`r`n- 在这里登记 ``$ModuleName`` 模块绑定的业务代码仓名称与 Git 地址。`r`n- 如果暂无绑定代码仓，可先保留本段作为占位。"
    }
    $normalized = $Section.Replace("## 项目代码绑定", "## 绑定项目代码")
    $normalized = $normalized.Replace("codes/workspace/", "codes/")
    $normalized = $normalized.Replace("cd codes/workspace", "cd codes")
    $normalized = $normalized.Replace("cd ../..", "cd ..")
    return $normalized.TrimEnd()
}

function Write-Agents {
    param(
        [string]$Path,
        [string]$ModuleName,
        [string]$TitleName,
        [string]$Binding,
        [bool]$HasProduct,
        [bool]$HasCodeReview
    )

    $productLine = if ($HasProduct) { "- 产品白皮书：``docs/domain/ProductWhitepaper.md```r`n" } else { "" }
    $reviewLine = if ($HasCodeReview) { "- 代码审查规则：``rules/code-review-rules.md```r`n" } else { "" }
    $reviewLoad = if ($HasCodeReview) { "- 需要执行代码审查：读 ``rules/code-review-rules.md```r`n" } else { "" }

    $content = @"
# $TitleName Agent 地图

## 模块目标

``$ModuleName/`` 是一个自包含 Harness 模块。这个文件只负责给 Agent 指路，不承载详细规则正文。

## 文档索引

- Harness 架构：``.harness/harness-overview.md``
- 目录边界：``.harness/directory-layout.md``
- 任务流转：``.harness/runtime-lifecycle.md``
- 代码总览：``docs/domain/TechWhitepaper.md``
$productLine- 需求目录：``docs/memory/demand/``
- 需求摘要：``docs/memory/summary/``
- 系统影响记忆：``docs/memory/memory.md``
- Agent 详细规则：``rules/agent-rules.md``
- 工程交付规则：``rules/engineering-rules.md``
$reviewLine
- 模块技能：``skills/README.md``

$Binding

## 按任务加载

- 需要查看、整理或更新某次需求材料：读 ``docs/memory/demand/``；每次需求应单独落到 ``docs/memory/demand/<demand-name>/``
- 需要 Agent 详细工作规则：读 ``rules/agent-rules.md``
- 需要工程交付规则：读 ``rules/engineering-rules.md``
- 需要记录需求改动对系统的影响：先读 ``rules/agent-rules.md`` 中的系统影响记忆规则，再更新 ``docs/memory/memory.md``,本动作需要主动触发
- 需要定位当前模块绑定的业务代码仓：先查看 ``codes/`` 下是否已有本地代码；如果本地不存在，再看本文件“绑定项目代码”章节获取仓库信息
- 调整目录、边界或放置规则：读 ``.harness/directory-layout.md``
- 需要了解当前绑定代码仓的整体技术结构和分工：读 ``docs/domain/TechWhitepaper.md``
- 调整任务链路、上下文流转或 Hook：读 ``.harness/runtime-lifecycle.md``

- 需要理解角色分工：读 ``skills/README.md``
$reviewLoad
## 硬边界

- 只处理 ``$ModuleName/`` 模块内部内容。
- 详细规则写进 ``.harness/``、``rules/`` 或 ``docs/`` 对应文档，不要继续把 ``AGENTS.md`` 扩成手册。
- 如果运行时能力尚未实现，不要把设计稿描述成已可执行能力。
- 当前模块绑定的项目代码如果本地不存在，应从对应 Git 地址拉取，并放在 ``codes/`` 目录下。
- 涉及需求变更对系统的影响时，必须按 ``rules/agent-rules.md`` 的约束更新 ``docs/memory/memory.md``。
"@
    Set-Content -LiteralPath $Path -Value $content.TrimEnd() -Encoding UTF8
}

function Write-Manifest {
    param(
        [string]$Path,
        [string]$ModuleName,
        [bool]$HasProduct
    )

    $productLine = if ($HasProduct) { "  product_whitepaper: docs/domain/ProductWhitepaper.md`r`n" } else { "" }
    $content = @"
name: $ModuleName
description: 自包含 Harness 模块
status: design-seeded
entrypoints:
  agent_map: AGENTS.md
  architecture: .harness/harness-overview.md
  directory_layout: .harness/directory-layout.md
  runtime_lifecycle: .harness/runtime-lifecycle.md
  tech_whitepaper: docs/domain/TechWhitepaper.md
$productLine  manifest: .module-manifest.yaml
memory_files:
  - AGENTS.md
  - docs/memory/memory.md
spec_paths:
  - docs/memory/demand
skill_paths:
  - skills/$ModuleName-analyst
  - skills/$ModuleName-operator
  - skills/$ModuleName-reviewer
context_paths:
  - docs/memory
workspace_paths:
  - codes
"@
    Set-Content -LiteralPath $Path -Value $content.TrimEnd() -Encoding UTF8
}

function Write-StandardHarnessDocs {
    param(
        [string]$Root,
        [string]$ModuleName
    )

    $directoryLayout = @"
# 目录布局

## 顶层规则

- ``.harness/`` 存放 Harness 结构、目录边界和任务流转说明。
- ``rules/`` 存放 Agent、工程交付和代码审查规则。
- ``docs/`` 存放领域白皮书、需求材料、摘要和系统影响记忆。
- ``skills/`` 存放模块私有的角色技能说明。
- ``codes/`` 存放本模块关联业务代码仓。

## 目录职责

- ``.harness/`` 存放 Harness 总览、目录布局和运行生命周期，不承载业务领域内容。
- ``rules/`` 存放跨任务复用的工作规则、工程规则和代码审查规则。
- ``docs/domain/`` 存放产品白皮书和技术白皮书等领域长期文档。
- ``docs/memory/demand/`` 按需求分目录存放问题定义、范围说明、设计文档、实施记录和 superpowers 产物。
- ``docs/memory/summary/`` 存放已归档需求摘要。
- ``docs/memory/memory.md`` 持续记录需求改动对系统接口造成的实际影响。
- ``skills/`` 存放角色化、阶段化的模块技能定义。
- ``codes/`` 存放实际业务代码和与实现直接相关的工作内容。

## 禁止混放

- 不要把临时任务产物直接丢进 ``docs/``。
- 不要继续新增 ``docs/prd/``、``docs/superpowers/`` 或旧的 ``docs/demand/``；需求过程材料统一归到 ``docs/memory/demand/<demand-name>/``。
- 不要恢复旧的 ``docs/architecture/``、``docs/rules/`` 或 ``docs/context/`` 目录；Harness 说明、规则和记忆分别归到 ``.harness/``、``rules/``、``docs/memory/``。
- 不要把详细规则继续堆进 ``AGENTS.md``；详细说明应写进 ``.harness/``、``rules/`` 或其他合适的长期文档。
- 不要把模块外部目录当成 ``$ModuleName`` 模块的运行时依赖。
"@

    $overview = @"
# Harness 总览

## 模块定位

``$ModuleName/`` 是一个自包含 Harness 模块。它自己管理记忆、规范、技能、上下文和运行骨架，不依赖模块外部的信息来完成内部说明。

## Harness 分层映射

- 导航入口层：``AGENTS.md``
- Harness 结构层：``.harness/``
- 规则层：``rules/``
- 领域文档层：``docs/domain/``
- 上下文与记忆层：``docs/memory/``
- 需求输入层：``docs/memory/demand/``
- 角色技能层：``skills/``
- 业务代码工作区：``codes/``

## 模块边界

所有属于 ``$ModuleName`` 模块的运行时结构、上下文规则和文档入口都应该落在 ``$ModuleName/`` 内部。

## 复用方式

这套结构可以作为一个独立模块的参考形状，在其他场景中按需复制和调整。

## AGENTS 定位

``AGENTS.md`` 在本模块里是地图，不是手册。它只保留入口、索引和按任务加载路径，详细规则沉到 ``rules/agent-rules.md`` 等文档中按需读取。

## 系统影响记忆

``docs/memory/memory.md`` 只用于持续记录每次需求改动对系统的实际影响；记录约束和格式说明放在 ``rules/agent-rules.md``。
"@

    $lifecycle = @"
# 运行生命周期

## 任务流转

1. 从 ``docs/memory/demand/<demand-name>/`` 读取当前需求的背景、目标和约束。
2. 从 ``AGENTS.md`` 判断当前任务该加载哪些详细文档。
3. 从 ``skills/`` 选择匹配当前任务的角色技能。
4. 在 ``docs/memory/`` 下读取或沉淀当前工作所需的需求、摘要和记忆材料。
5. 把本次需求相关的背景、设计文档、实施记录和 superpowers 产物直接落到 ``docs/memory/demand/<demand-name>/``，把代码相关产物落到 ``codes/``。
6. 如果本次需求改动影响了系统接口，还要按规则更新 ``docs/memory/memory.md``。
7. 需求上线后，将对应 ``docs/memory/demand/<demand-name>/`` 的关键信息归档到 ``docs/memory/summary/``。

## 质量关卡

- 校验规则必须显式存在，不能靠隐含约定。
- 大体积的临时产物应留在 ``codes/``，需要时再总结到其他位置。
- 一条规则只要会跨任务复用，就应该沉淀到 ``.harness/`` 或 ``rules/`` 中对应文档，由 ``AGENTS.md`` 提供入口。
- 需求变更对系统的影响必须落在 ``docs/memory/memory.md``，具体记录约束以 ``rules/agent-rules.md`` 为准。
- 需求上线后的归档应优先沉淀到 ``docs/memory/summary/``，不要让历史需求长期散落在活动目录里。
"@

    Set-Content -LiteralPath (Join-Path $Root ".harness\directory-layout.md") -Value $directoryLayout.TrimEnd() -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $Root ".harness\harness-overview.md") -Value $overview.TrimEnd() -Encoding UTF8
    Set-Content -LiteralPath (Join-Path $Root ".harness\runtime-lifecycle.md") -Value $lifecycle.TrimEnd() -Encoding UTF8
}

$root = [System.IO.Path]::GetFullPath($ModuleRoot)
if (-not (Test-Path -LiteralPath (Join-Path $root "AGENTS.md"))) {
    throw "AGENTS.md not found. Run this script from a Harness module root."
}
if (-not (Test-Path -LiteralPath (Join-Path $root ".module-manifest.yaml"))) {
    throw ".module-manifest.yaml not found. Run this script from a Harness module root."
}

$moduleName = Split-Path -Leaf $root
$oldAgents = Get-Content -LiteralPath (Join-Path $root "AGENTS.md") -Raw
$title = $moduleName.Substring(0, 1).ToUpper() + $moduleName.Substring(1)
if ($oldAgents.Split("`n")[0].StartsWith("# ")) {
    $oldTitle = $oldAgents.Split("`n")[0].Substring(2).Trim().Replace(" Agent 地图", "").Trim()
    if ($oldTitle) {
        $title = $oldTitle
    }
}

$binding = Get-Section -Text $oldAgents -StartHeading "## 绑定项目代码" -NextHeading "## 按任务加载"
if (-not $binding) {
    $binding = Get-Section -Text $oldAgents -StartHeading "## 项目代码绑定" -NextHeading "## 按任务加载"
}
$binding = Normalize-BindingSection -Section $binding -ModuleName $moduleName

$SkippedItems = @()
foreach ($dir in @(".harness", "rules", "docs\domain", "docs\memory\demand", "docs\memory\summary", "codes")) {
    Ensure-Dir -Path (Join-Path $root $dir)
}

Move-FileIfNeeded (Join-Path $root "docs\architecture\directory-layout.md") (Join-Path $root ".harness\directory-layout.md") | Out-Null
Move-FileIfNeeded (Join-Path $root "docs\architecture\harness-overview.md") (Join-Path $root ".harness\harness-overview.md") | Out-Null
Move-FileIfNeeded (Join-Path $root "docs\architecture\runtime-lifecycle.md") (Join-Path $root ".harness\runtime-lifecycle.md") | Out-Null
Move-FileIfNeeded (Join-Path $root "docs\architecture\code-overview.md") (Join-Path $root "docs\domain\TechWhitepaper.md") | Out-Null
Move-FileIfNeeded (Join-Path $root "docs\whitepaper\ProductWhitepaper.md") (Join-Path $root "docs\domain\ProductWhitepaper.md") | Out-Null
Move-FileIfNeeded (Join-Path $root "docs\context\memory\memory.md") (Join-Path $root "docs\memory\memory.md") | Out-Null

foreach ($pair in @(
    @("docs\rules\agent-rules.md", "rules\agent-rules.md"),
    @("docs\rules\engineering-rules.md", "rules\engineering-rules.md"),
    @("docs\rules\code-review-rules.md", "rules\code-review-rules.md"),
    @("docs\architecture\agent-rules.md", "rules\agent-rules.md"),
    @("docs\architecture\engineering-rules.md", "rules\engineering-rules.md"),
    @("docs\architecture\code-review-rules.md", "rules\code-review-rules.md")
)) {
    Move-FileIfNeeded (Join-Path $root $pair[0]) (Join-Path $root $pair[1]) | Out-Null
}

Move-DirContentsIfNeeded (Join-Path $root "docs\demand") (Join-Path $root "docs\memory\demand") | Out-Null
Move-DirContentsIfNeeded (Join-Path $root "docs\context\summaries") (Join-Path $root "docs\memory\summary") | Out-Null
Move-DirContentsIfNeeded (Join-Path $root "docs\context\summary") (Join-Path $root "docs\memory\summary") | Out-Null
Move-DirContentsIfNeeded (Join-Path $root "codes\workspace") (Join-Path $root "codes") | Out-Null

if (-not (Test-Path -LiteralPath (Join-Path $root "docs\memory\memory.md"))) {
    Set-Content -LiteralPath (Join-Path $root "docs\memory\memory.md") -Value "# 系统影响记忆`r`n`r`n这个文档只用于记录每次需求改动对系统造成的实际影响，不承载规则说明。`r`n`r`n## 变更记录`r`n`r`n- 暂无记录" -Encoding UTF8
}

Write-StandardHarnessDocs -Root $root -ModuleName $moduleName

$map = @{
    "docs/context/summaries" = "docs/memory/summary"
    "docs/context/memory/memory.md" = "docs/memory/memory.md"
    "docs/architecture/code-overview.md" = "docs/domain/TechWhitepaper.md"
    "docs/architecture/harness-overview.md" = ".harness/harness-overview.md"
    "docs/architecture/directory-layout.md" = ".harness/directory-layout.md"
    "docs/architecture/runtime-lifecycle.md" = ".harness/runtime-lifecycle.md"
    "docs/architecture/agent-rules.md" = "rules/agent-rules.md"
    "docs/architecture/engineering-rules.md" = "rules/engineering-rules.md"
    "docs/rules/agent-rules.md" = "rules/agent-rules.md"
    "docs/rules/engineering-rules.md" = "rules/engineering-rules.md"
    "docs/rules/code-review-rules.md" = "rules/code-review-rules.md"
    "docs/context" = "docs/memory"
    "docs/demand" = "docs/memory/demand"
    "codes/workspace" = "codes"
}

Get-ChildItem -LiteralPath $root -Recurse -File -Include *.md,*.yaml,*.yml -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\codes\\[^\\]+\\" } |
    ForEach-Object { Replace-InTextFile -Path $_.FullName -Map $map }

$hasProduct = Test-Path -LiteralPath (Join-Path $root "docs\domain\ProductWhitepaper.md")
$hasReview = Test-Path -LiteralPath (Join-Path $root "rules\code-review-rules.md")
Write-Agents -Path (Join-Path $root "AGENTS.md") -ModuleName $moduleName -TitleName $title -Binding $binding -HasProduct $hasProduct -HasCodeReview $hasReview
Write-Manifest -Path (Join-Path $root ".module-manifest.yaml") -ModuleName $moduleName -HasProduct $hasProduct
Set-Content -LiteralPath (Join-Path $root "CLAUDE.md") -Value "AGENTS.md" -Encoding UTF8

Set-Content -LiteralPath (Join-Path $root ".gitignore") -Value "# IDE`r`n.idea/`r`n.claude/`r`n`r`n# 业务代码工作区`r`ncodes/*`r`n!codes/.gitkeep" -Encoding UTF8

foreach ($obsolete in @(
    "README.md",
    "codes\README.md",
    "codes\workspace\README.md",
    "docs\context\README.md",
    "docs\context\memory\README.md",
    "docs\context\sessions\README.md",
    "docs\context\summaries\README.md",
    "docs\context\system\README.md",
    "docs\demand\README.md"
)) {
    Remove-FileIfExists -Path (Join-Path $root $obsolete)
}

foreach ($placeholder in @(
    "docs\memory\demand\README.md",
    "docs\memory\summary\README.md"
)) {
    Remove-FileIfExists -Path (Join-Path $root $placeholder)
}

foreach ($dir in @(
    "codes\workspace",
    "docs\architecture",
    "docs\rules",
    "docs\context\memory",
    "docs\context\sessions",
    "docs\context\summaries",
    "docs\context\system",
    "docs\context",
    "docs\demand",
    "docs\whitepaper"
)) {
    Remove-EmptyDir -Path (Join-Path $root $dir)
}

foreach ($dir in @("codes", "docs\memory\demand", "docs\memory\summary")) {
    $full = Join-Path $root $dir
    if (Test-Path -LiteralPath $full -PathType Container) {
        $items = Get-ChildItem -LiteralPath $full -Force
        if ($items.Count -eq 0) {
            New-Item -ItemType File -Path (Join-Path $full ".gitkeep") -Force | Out-Null
        }
    }
}

Write-Host "Migrated legacy Harness module: $moduleName"
if ($SkippedItems.Count -gt 0) {
    Write-Host "Skipped existing destinations:"
    $SkippedItems | Sort-Object | ForEach-Object { Write-Host " - $_" }
}
Write-Host "Next verification:"
Write-Host '  rg -n "docs/(architecture|rules|context|whitepaper|demand)|codes/workspace" . --glob "!codes/**" -g "*.md" -g "*.yaml" -g "*.yml"'
Write-Host "  git diff --check"
