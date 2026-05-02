@echo off
setlocal
cd /d "%~dp0"
echo Starting JARVIS...
start "JARVIS" py -3.14 -m jarvis.main
endlocal

