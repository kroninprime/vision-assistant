$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupDir = [Environment]::GetFolderPath("Startup")
$launcherPath = Join-Path $startupDir "JarvisLauncher.cmd"

$content = @"
@echo off
cd /d "$projectDir"
start "JARVIS" py -3.14 -m jarvis.main
"@

Set-Content -Path $launcherPath -Value $content -Encoding ASCII
Write-Host "Startup launcher created at: $launcherPath"
Write-Host "JARVIS will auto-start at user logon without Cursor."

