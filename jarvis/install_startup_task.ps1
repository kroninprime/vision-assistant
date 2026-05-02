$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = "JarvisVoiceAssistant"
$pythonCmd = "py -3.14 -m jarvis.main"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -Command `"cd '$projectDir'; $pythonCmd`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0) -AllowStartIfOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Start Jarvis voice assistant at logon" -Force | Out-Null

Write-Host "Startup task installed: $taskName"
Write-Host "Jarvis will now start automatically at Windows logon."

