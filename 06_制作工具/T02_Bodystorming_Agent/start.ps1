$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'dist\index.html'))) {
    Write-Host 'Frontend not built. Run npm install and npm run build first.'
    Read-Host 'Press Enter to exit'
    exit 1
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python server.py
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 server.py
} else {
    Write-Host 'Python 3.10+ is required. Install Python and try again.'
}
Read-Host 'Press Enter to close'
