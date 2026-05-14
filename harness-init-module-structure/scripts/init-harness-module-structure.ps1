param(
    [Parameter(Mandatory = $true)]
    [string]$TargetDir,

    [string]$ModuleName
)

$ErrorActionPreference = "Stop"

function Get-RelativePathCompat {
    param(
        [string]$BasePath,
        [string]$ChildPath
    )

    $baseFull = [System.IO.Path]::GetFullPath($BasePath)
    $childFull = [System.IO.Path]::GetFullPath($ChildPath)

    if (-not $baseFull.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $baseFull += [System.IO.Path]::DirectorySeparatorChar
    }

    $baseUri = New-Object System.Uri($baseFull)
    $childUri = New-Object System.Uri($childFull)
    $relativeUri = $baseUri.MakeRelativeUri($childUri)
    return [System.Uri]::UnescapeDataString($relativeUri.ToString()).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

$textExtensions = @(
    ".md",
    ".yaml",
    ".yml",
    ".txt",
    ".ps1",
    ".json"
)

function Normalize-ModuleName {
    param(
        [string]$InputName
    )

    $trimmed = $InputName.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) {
        throw "ModuleName cannot be empty."
    }

    return $trimmed
}

function Replace-TemplateTokens {
    param(
        [string]$FilePath,
        [string]$ResolvedModuleName
    )

    $extension = [System.IO.Path]::GetExtension($FilePath).ToLowerInvariant()
    if ($textExtensions -notcontains $extension) {
        return
    }

    $content = Get-Content -LiteralPath $FilePath -Raw
    $updated = $content.Replace("__MODULE_NAME__", $ResolvedModuleName)
    if ($updated -ne $content) {
        Set-Content -LiteralPath $FilePath -Value $updated -Encoding UTF8
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillDir = Split-Path -Parent $scriptDir
$templateRoot = (Resolve-Path (Join-Path $skillDir "assets\\template")).Path
$resolvedTarget = [System.IO.Path]::GetFullPath($TargetDir)

if (-not $ModuleName) {
    $ModuleName = Read-Host "Enter module name"
}

$resolvedModuleName = Normalize-ModuleName -InputName $ModuleName

if ($resolvedTarget -eq $templateRoot) {
    throw "TargetDir cannot be the packaged template root."
}

if (-not (Test-Path -LiteralPath $resolvedTarget)) {
    New-Item -ItemType Directory -Path $resolvedTarget | Out-Null
}

$copied = New-Object System.Collections.Generic.List[string]
$createdDirs = New-Object System.Collections.Generic.List[string]

$requiredDirs = @(
    ".harness",
    "rules",
    "docs",
    "docs\domain",
    "docs\memory",
    "docs\memory\demand",
    "docs\memory\summary",
    "codes",
    "skills"
)
foreach ($relativePath in $requiredDirs) {
    $destination = Join-Path $resolvedTarget $relativePath
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
        $createdDirs.Add($relativePath)
    }
}

$directories = Get-ChildItem -LiteralPath $templateRoot -Recurse -Directory | Sort-Object FullName
foreach ($directory in $directories) {
    $relativePath = Get-RelativePathCompat -BasePath $templateRoot -ChildPath $directory.FullName
    $relativePath = $relativePath.Replace("__MODULE_NAME__", $resolvedModuleName)
    $destination = Join-Path $resolvedTarget $relativePath
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
        $createdDirs.Add($relativePath)
    }
}

$files = Get-ChildItem -LiteralPath $templateRoot -Recurse -File | Sort-Object FullName
foreach ($file in $files) {
    $relativePath = Get-RelativePathCompat -BasePath $templateRoot -ChildPath $file.FullName
    $relativePath = $relativePath.Replace("__MODULE_NAME__", $resolvedModuleName)
    $destination = Join-Path $resolvedTarget $relativePath
    $destinationDir = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationDir)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
    Replace-TemplateTokens -FilePath $destination -ResolvedModuleName $resolvedModuleName
    $copied.Add($relativePath)
}

Write-Host "Initialized harness module '$resolvedModuleName' from template at: $resolvedTarget"
if ($createdDirs.Count -gt 0) {
    Write-Host "Created directories:"
    $createdDirs | ForEach-Object { Write-Host " - $_" }
}
Write-Host "Copied files:"
$copied | ForEach-Object { Write-Host " - $_" }
