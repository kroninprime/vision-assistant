$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$modelsDir = Join-Path $projectDir "models"
$modelName = "vosk-model-small-en-us-0.15"
$zipPath = Join-Path $modelsDir "$modelName.zip"
$extractPath = Join-Path $modelsDir $modelName
$url = "https://alphacephei.com/vosk/models/$modelName.zip"

New-Item -ItemType Directory -Path $modelsDir -Force | Out-Null

if (Test-Path $extractPath) {
    Write-Host "Model already exists at $extractPath"
    exit 0
}

Write-Host "Downloading $modelName ..."
Invoke-WebRequest -Uri $url -OutFile $zipPath

Write-Host "Extracting model ..."
Expand-Archive -Path $zipPath -DestinationPath $modelsDir -Force
Remove-Item $zipPath -Force

Write-Host "Vosk model installed at $extractPath"
