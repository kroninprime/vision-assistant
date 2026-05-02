$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt

Write-Host "Starting Jarvis daemon..." -ForegroundColor Cyan
Write-Host "Double-tap Ctrl anywhere to wake Jarvis." -ForegroundColor Green

python ".\jarvis_daemon.py"
