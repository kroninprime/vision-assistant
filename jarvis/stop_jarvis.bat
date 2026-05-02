@echo off
echo Stopping JARVIS...
taskkill /FI "WINDOWTITLE eq JARVIS" /T /F >nul 2>&1
taskkill /IM python.exe /FI "WINDOWTITLE eq JARVIS" /T /F >nul 2>&1
echo Done.

