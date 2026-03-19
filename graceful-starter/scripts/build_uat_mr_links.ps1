param(
    [string]$RootDir = (Split-Path -Parent $PSScriptRoot),
    [string]$ProjectsFile,
    [string]$GitsFile,
    [string]$OutputFile,
    [string]$SourceBranch = "feature/优雅上下线",
    [string]$TargetBranch = "uat"
)

$ErrorActionPreference = "Stop"

if (-not $OutputFile) {
    $OutputFile = Join-Path $RootDir "uat_mr_links.md"
}

function Get-TrimmedLines {
    param([string]$Path)

    Get-Content -Path $Path |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
}

function Get-ProjectFromGitUrl {
    param([string]$GitUrl)

    return [System.IO.Path]::GetFileNameWithoutExtension(($GitUrl -split "/")[-1])
}

function Convert-ToWebRepoUrl {
    param([string]$GitUrl)

    if ($GitUrl -match "^git@([^:]+):(.+?)(\.git)?$") {
        $host = $matches[1]
        $path = $matches[2]
        return "http://$host/$path"
    }

    if ($GitUrl -match "^(https?://.+?)(\.git)?$") {
        return $matches[1]
    }

    throw "无法解析 Git 地址: $GitUrl"
}

function Build-RepoMap {
    param([string[]]$GitUrls)

    $map = @{}
    foreach ($gitUrl in $GitUrls) {
        $project = Get-ProjectFromGitUrl -GitUrl $gitUrl
        if (-not $map.ContainsKey($project)) {
            $map[$project] = $gitUrl
        }
    }
    return $map
}

function Resolve-GitsFile {
    param([string]$ConfiguredPath)

    if ($ConfiguredPath) {
        if (-not (Test-Path $ConfiguredPath)) {
            throw "Git 地址文件不存在: $ConfiguredPath"
        }
        return $ConfiguredPath
    }

    $candidates = @(
        (Join-Path $RootDir "gits.txt")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    throw "未找到 Git 地址文件，请在 $RootDir 下提供 gits.txt，或通过 -GitsFile 指定"
}

function Resolve-Projects {
    param(
        [string]$ProjectsFilePath,
        [hashtable]$RepoMap
    )

    if ($ProjectsFilePath -and (Test-Path $ProjectsFilePath)) {
        $projects = Get-TrimmedLines -Path $ProjectsFilePath
        $missing = @($projects | Where-Object { -not $RepoMap.ContainsKey($_) })
        if ($missing.Count -gt 0) {
            throw "以下项目缺少 Git 地址: $($missing -join ', ')"
        }
        return $projects
    }

    return @($RepoMap.Keys | Sort-Object)
}

$GitsFile = Resolve-GitsFile -ConfiguredPath $GitsFile
$gitUrls = Get-TrimmedLines -Path $GitsFile
$repoMap = Build-RepoMap -GitUrls $gitUrls
$projects = Resolve-Projects -ProjectsFilePath $ProjectsFile -RepoMap $repoMap

$sourceEncoded = [System.Uri]::EscapeDataString($SourceBranch)
$targetEncoded = [System.Uri]::EscapeDataString($TargetBranch)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("| 项目 | MR链接 |")
$lines.Add("| --- | --- |")

foreach ($project in $projects) {
    $repoUrl = Convert-ToWebRepoUrl -GitUrl $repoMap[$project]
    $mrUrl = "$repoUrl/-/merge_requests/new?merge_request%5Bsource_branch%5D=$sourceEncoded&merge_request%5Btarget_branch%5D=$targetEncoded"
    $lines.Add("| $project | $mrUrl |")
}

Set-Content -Path $OutputFile -Value $lines -Encoding UTF8
Write-Output "已生成: $OutputFile"
