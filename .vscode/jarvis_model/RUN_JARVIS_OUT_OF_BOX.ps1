$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "== Jarvis Out-of-Box Boot ==" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
  python -m venv .venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example" -ForegroundColor Green
}

$ollamaOk = $false
try {
  $null = Get-Command ollama -ErrorAction Stop
  $ollamaOk = $true
} catch {
  Write-Host "Ollama not found. Running in built-in local mode (no external AI engine)." -ForegroundColor Yellow
}

if ($ollamaOk) {
  Write-Host "Ollama detected. Starting local AI server..." -ForegroundColor Yellow
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama serve"
}

Write-Host "Starting Jarvis server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; uvicorn app:app --reload --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8000/"

Write-Host "Jarvis boot sequence started." -ForegroundColor Green
Write-Host "Capabilities endpoint: http://127.0.0.1:8000/capabilities" -ForegroundColor Cyan
