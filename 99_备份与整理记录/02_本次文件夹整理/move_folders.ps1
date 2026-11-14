$ErrorActionPreference = 'Stop'
$workspaceRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path.TrimEnd('\')
$plan = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '迁移计划.json') | ConvertFrom-Json
$workspacePrefix = $workspaceRoot + '\'
$journal = Join-Path $PSScriptRoot '移动日志.jsonl'

function Assert-InWorkspace([string]$candidate) {
    $full = [System.IO.Path]::GetFullPath($candidate)
    if (-not $full.StartsWith($workspacePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "路径超出工作区：$full"
    }
    return $full
}

foreach ($item in $plan.moves) {
    $source = Assert-InWorkspace (Join-Path $workspaceRoot $item.source)
    $destination = Assert-InWorkspace (Join-Path $workspaceRoot $item.destination)
    if (-not (Test-Path -LiteralPath $source)) {
        throw "源路径不存在：$source"
    }
    $resolvedSource = (Resolve-Path -LiteralPath $source).Path
    $null = Assert-InWorkspace $resolvedSource
    if (Test-Path -LiteralPath $destination) {
        throw "目标已存在，停止以避免合并或覆盖：$destination"
    }
    if ($destination.StartsWith($resolvedSource.TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw '目标不能位于源目录内。'
    }
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Move-Item -LiteralPath $resolvedSource -Destination $destination -ErrorAction Stop
    [ordered]@{source=$item.source;destination=$item.destination;time=(Get-Date).ToString('o');status='moved'} |
        ConvertTo-Json -Compress | Add-Content -LiteralPath $journal -Encoding utf8
    Write-Output "已移动：$($item.source) -> $($item.destination)"
}

$emptyWrapper = Assert-InWorkspace (Join-Path $workspaceRoot '创作工作区')
if ((Test-Path -LiteralPath $emptyWrapper) -and (@(Get-ChildItem -Force -LiteralPath $emptyWrapper).Count -eq 0)) {
    Remove-Item -LiteralPath $emptyWrapper -ErrorAction Stop
}
Write-Output '文件夹移动完成。'
