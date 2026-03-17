param(
    [string]$RootDir = (Split-Path -Parent $PSScriptRoot),
    [string]$ProjectsFile,
    [string]$GitsFile,
    [string]$ReposDir,
    [string]$FeatureBranch = "feature/优雅上下线",
    [string]$BaseBranch = "master",
    [switch]$RebuildFeature
)

$ErrorActionPreference = "Stop"

if (-not $ProjectsFile) {
    $ProjectsFile = Join-Path $RootDir "projects.txt"
}
if (-not $GitsFile) {
    $GitsFile = Join-Path $RootDir "gits.txt"
}
if (-not $ReposDir) {
    $ReposDir = Join-Path $RootDir "projects"
}

function Get-TrimmedLines {
    param([string]$Path)

    Get-Content -Path $Path |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
}

function Build-RepoMap {
    param([string[]]$GitUrls)

    $map = @{}
    foreach ($gitUrl in $GitUrls) {
        $name = [System.IO.Path]::GetFileNameWithoutExtension(($gitUrl -split "/")[-1])
        if (-not $map.ContainsKey($name)) {
            $map[$name] = $gitUrl
        }
    }
    return $map
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

function Test-CleanWorktree {
    param([string]$RepoPath)

    Push-Location $RepoPath
    try {
        $status = git status --porcelain
        return [string]::IsNullOrWhiteSpace(($status -join ""))
    }
    finally {
        Pop-Location
    }
}

function Ensure-RemoteBranch {
    param(
        [string]$RepoPath,
        [string]$BranchName
    )

    Push-Location $RepoPath
    try {
        $remoteHit = git ls-remote --heads origin $BranchName
        return -not [string]::IsNullOrWhiteSpace(($remoteHit -join ""))
    }
    finally {
        Pop-Location
    }
}

function Ensure-RepoReady {
    param(
        [string]$Project,
        [string]$GitUrl
    )

    $repoPath = Join-Path $ReposDir $Project
    if (-not (Test-Path $repoPath)) {
        git clone $GitUrl $repoPath
    }

    Push-Location $repoPath
    try {
        git fetch --all --prune

        if (-not (Test-CleanWorktree -RepoPath $repoPath)) {
            throw "工作区不干净，无法切换或重建分支: $Project"
        }

        $remoteBase = "origin/$BaseBranch"
        $baseExists = git rev-parse --verify $remoteBase 2>$null
        if (-not $baseExists) {
            throw "缺少远端基线分支 ${remoteBase}: $Project"
        }

        if ($RebuildFeature) {
            git checkout -B $BaseBranch $remoteBase | Out-Null

            $localBranch = git branch --list $FeatureBranch
            if (-not [string]::IsNullOrWhiteSpace($localBranch)) {
                git branch -D $FeatureBranch | Out-Null
            }

            if (Ensure-RemoteBranch -RepoPath $repoPath -BranchName $FeatureBranch) {
                try {
                    git push origin ":refs/heads/$FeatureBranch" | Out-Null
                }
                catch {
                    Write-Warning ("远端删除分支失败，请人工确认: {0} {1}" -f $Project, $FeatureBranch)
                }
            }

            git checkout -b $FeatureBranch $remoteBase | Out-Null
        }
        else {
            $branchExists = git branch --list $FeatureBranch
            if ([string]::IsNullOrWhiteSpace($branchExists)) {
                if (Ensure-RemoteBranch -RepoPath $repoPath -BranchName $FeatureBranch) {
                    git checkout -B $FeatureBranch "origin/$FeatureBranch" | Out-Null
                }
                else {
                    git checkout -b $FeatureBranch $remoteBase | Out-Null
                }
            }
            else {
                git checkout $FeatureBranch | Out-Null
            }
        }

        [PSCustomObject]@{
            Project = $Project
            RepoPath = $repoPath
            GitUrl = $GitUrl
            FeatureBranch = $FeatureBranch
            BaseBranch = $BaseBranch
            RebuildFeature = [bool]$RebuildFeature
        }
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path $ReposDir)) {
    New-Item -ItemType Directory -Path $ReposDir | Out-Null
}

$gitUrls = Get-TrimmedLines -Path $GitsFile
$repoMap = Build-RepoMap -GitUrls $gitUrls
$projects = Resolve-Projects -ProjectsFilePath $ProjectsFile -RepoMap $repoMap

$results = foreach ($project in $projects) {
    Ensure-RepoReady -Project $project -GitUrl $repoMap[$project]
}

$results | Sort-Object Project | Format-Table -AutoSize
