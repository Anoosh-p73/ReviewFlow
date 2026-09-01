[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$failures = [System.Collections.Generic.List[string]]::new()

function Add-Failure {
    param([Parameter(Mandatory)][string]$Message)

    $failures.Add($Message)
}

$requiredFiles = @(
    '.editorconfig'
    '.env.example'
    '.node-version'
    '.python-version'
    'AGENTS.md'
    'README.md'
    'docs/architecture.md'
    'docs/ci-cd.md'
    'docs/development.md'
    'docs/roadmap.md'
    'package.json'
    'pnpm-lock.yaml'
    'pnpm-workspace.yaml'
)

foreach ($relativePath in $requiredFiles) {
    $absolutePath = Join-Path $repositoryRoot $relativePath
    if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
        Add-Failure "Required planning file is missing: $relativePath"
    }
}

$packagePath = Join-Path $repositoryRoot 'package.json'
if (Test-Path -LiteralPath $packagePath -PathType Leaf) {
    try {
        $packageManifest = Get-Content -Raw -LiteralPath $packagePath |
            ConvertFrom-Json -ErrorAction Stop

        if ($packageManifest.private -ne $true) {
            Add-Failure 'Root package.json must remain private.'
        }
        if ($packageManifest.packageManager -notmatch '^pnpm@\d+\.\d+\.\d+$') {
            Add-Failure 'Root package.json must pin an exact pnpm version.'
        }
        if (-not $packageManifest.scripts.check) {
            Add-Failure 'Root package.json must expose the check command.'
        }
    } catch {
        Add-Failure "Root package.json is not valid JSON: $($_.Exception.Message)"
    }
}

$roadmapPath = Join-Path $repositoryRoot 'docs/roadmap.md'
if (Test-Path -LiteralPath $roadmapPath -PathType Leaf) {
    $roadmap = Get-Content -Raw -LiteralPath $roadmapPath
    $taskMatches = [regex]::Matches(
        $roadmap,
        '(?m)^### Task (?<number>\d+) - .+$'
    )

    if ($taskMatches.Count -lt 35 -or $taskMatches.Count -gt 50) {
        Add-Failure (
            'Roadmap must contain between 35 and 50 tasks; found ' +
            $taskMatches.Count
        )
    }

    $requiredTaskSections = @(
        'Goal'
        'Main implementation work'
        'Acceptance criteria'
        'Tests expected'
        'Explicitly deferred'
    )

    for ($index = 0; $index -lt $taskMatches.Count; $index++) {
        $match = $taskMatches[$index]
        $taskNumber = [int]$match.Groups['number'].Value
        $expectedNumber = $index + 1

        if ($taskNumber -ne $expectedNumber) {
            Add-Failure (
                "Roadmap task numbering is not sequential: expected " +
                "$expectedNumber, found $taskNumber"
            )
        }

        $endIndex = if ($index + 1 -lt $taskMatches.Count) {
            $taskMatches[$index + 1].Index
        } else {
            $roadmap.Length
        }
        $taskText = $roadmap.Substring($match.Index, $endIndex - $match.Index)

        foreach ($section in $requiredTaskSections) {
            $sectionPattern = '(?m)^\*\*' + [regex]::Escape($section) + ':\*\*'
            $sectionCount = [regex]::Matches($taskText, $sectionPattern).Count
            if ($sectionCount -ne 1) {
                Add-Failure (
                    "Task $taskNumber must contain exactly one '$section' " +
                    "section; found $sectionCount"
                )
            }
        }
    }

    foreach ($detailedTaskNumber in 1..5) {
        $taskIndex = $detailedTaskNumber - 1
        if ($taskIndex -ge $taskMatches.Count) {
            break
        }

        $startIndex = $taskMatches[$taskIndex].Index
        $endIndex = if ($taskIndex + 1 -lt $taskMatches.Count) {
            $taskMatches[$taskIndex + 1].Index
        } else {
            $roadmap.Length
        }
        $taskText = $roadmap.Substring($startIndex, $endIndex - $startIndex)

        foreach ($section in @('Manual verification', 'Failure and design notes')) {
            $sectionPattern = '(?m)^\*\*' + [regex]::Escape($section) + ':\*\*'
            if (-not [regex]::IsMatch($taskText, $sectionPattern)) {
                Add-Failure "Detailed Task $detailedTaskNumber is missing '$section'"
            }
        }
    }
}

$candidateFiles = & git -C $repositoryRoot ls-files --cached --others --exclude-standard
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to enumerate repository files with git.'
}

$markdownFiles = $candidateFiles |
    Where-Object { [System.IO.Path]::GetExtension($_) -eq '.md' } |
    ForEach-Object { Get-Item -LiteralPath (Join-Path $repositoryRoot $_) }

foreach ($markdownFile in $markdownFiles) {
    $content = Get-Content -Raw -LiteralPath $markdownFile.FullName
    $linkMatches = [regex]::Matches(
        $content,
        '\[[^\]]+\]\((?<target>[^)]+)\)'
    )

    foreach ($linkMatch in $linkMatches) {
        $target = $linkMatch.Groups['target'].Value
        if (
            $target.StartsWith('#') -or
            $target -match '^[a-zA-Z][a-zA-Z0-9+.-]*:'
        ) {
            continue
        }

        $pathWithoutAnchor = $target.Split('#', 2)[0]
        if ([string]::IsNullOrWhiteSpace($pathWithoutAnchor)) {
            continue
        }

        $decodedPath = [System.Uri]::UnescapeDataString($pathWithoutAnchor)
        $linkPath = Join-Path $markdownFile.DirectoryName $decodedPath
        if (-not (Test-Path -LiteralPath $linkPath)) {
            $relativeMarkdownPath = [System.IO.Path]::GetRelativePath(
                $repositoryRoot,
                $markdownFile.FullName
            )
            Add-Failure "Broken local link in ${relativeMarkdownPath}: $target"
        }
    }
}

$textFileExtensions = @(
    '.editorconfig'
    '.env.example'
    '.gitattributes'
    '.gitignore'
    '.node-version'
    '.python-version'
    '.json'
    '.md'
    '.mjs'
    '.ps1'
    '.yaml'
    '.yml'
)
foreach ($relativePath in $candidateFiles) {
    $absolutePath = Join-Path $repositoryRoot $relativePath
    if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
        continue
    }

    $fileName = [System.IO.Path]::GetFileName($relativePath)
    $extension = [System.IO.Path]::GetExtension($relativePath)
    if ($fileName -notin $textFileExtensions -and $extension -notin $textFileExtensions) {
        continue
    }

    $lineNumber = 0
    foreach ($line in Get-Content -LiteralPath $absolutePath) {
        $lineNumber++
        if ($line -match '[ \t]+$') {
            Add-Failure "Trailing whitespace: ${relativePath}:$lineNumber"
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Error (
        "Planning validation failed:`n- " +
        ($failures -join "`n- ")
    )
    exit 1
}

Write-Host (
    "Planning validation passed: $($taskMatches.Count) sequential roadmap " +
    'tasks, required sections, local links, and repository whitespace.'
)
