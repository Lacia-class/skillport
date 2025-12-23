@echo off
setlocal
setx SKILLPORT_EMBEDDING_PROVIDER "local" >nul
setx SKILLPORT_EMBEDDING_BASE_URL "http://localhost:11434/v1" >nul
setx SKILLPORT_EMBEDDING_MODEL "bge-m3" >nul
echo Switched embedding to LOCAL (Ollama).
echo Note: restart terminals/IDEs to pick up new env vars.
pause
