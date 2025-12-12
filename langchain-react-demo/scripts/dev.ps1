param(
    [string]$ApiBase = "http://127.0.0.1:8000",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvDir = Join-Path $backendDir ".venv"
$pythonExe = Join-Path $venvDir "Scripts/python.exe"

function Invoke-WithLocation {
    param(
        [string]$Path,
        [ScriptBlock]$Script
    )
    Push-Location $Path
    try {
        & $Script
    }
    finally {
        Pop-Location
    }
}

function Ensure-BackendEnv {
    if (-not (Test-Path $venvDir)) {
        Write-Host "Creating backend virtual environment in $venvDir" -ForegroundColor Cyan
        Invoke-WithLocation -Path $backendDir -Script { python -m venv .venv }
    }

    Write-Host "Installing backend requirements" -ForegroundColor Cyan
    & $pythonExe -m pip install -r (Join-Path $repoRoot "requirements.txt")
}

function Ensure-FrontendDeps {
    Write-Host "Installing frontend dependencies" -ForegroundColor Cyan
    Invoke-WithLocation -Path $frontendDir -Script { npm install }
}

if (-not $SkipInstall) {
    Ensure-BackendEnv
    Ensure-FrontendDeps
}

$backendCommand = @"
Set-Location "$backendDir"
& "$pythonExe" -m uvicorn app:app --reload
"@

$frontendCommand = @"
Set-Location "$frontendDir"
`$env:VITE_API_BASE = "$ApiBase"
npm run dev
"@

Write-Host "Launching FastAPI backend..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $backendCommand

Write-Host "Launching Vite frontend (VITE_API_BASE=$ApiBase)..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Both processes started in new terminals. Press Ctrl+C to exit this helper." -ForegroundColor Yellow
