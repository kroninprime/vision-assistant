$ErrorActionPreference = "SilentlyContinue"
$taskName = "JarvisVoiceAssistant"

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
Write-Host "Startup task removed: $taskName"

