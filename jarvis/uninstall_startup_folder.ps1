$ErrorActionPreference = "SilentlyContinue"

$startupDir = [Environment]::GetFolderPath("Startup")
$launcherPath = Join-Path $startupDir "JarvisLauncher.cmd"

if (Test-Path $launcherPath) {
    Remove-Item $launcherPath -Force
    Write-Host "Removed startup launcher: $launcherPath"
} else {
    Write-Host "No startup launcher found."
}

