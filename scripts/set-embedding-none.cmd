@echo off
setlocal
setx SKILLPORT_EMBEDDING_PROVIDER "none" >nul
setx SKILLPORT_EMBEDDING_BASE_URL "" >nul
setx SKILLPORT_EMBEDDING_MODEL "" >nul
echo Switched embedding to NONE (FTS only).
echo Note: restart terminals/IDEs to pick up new env vars.
pause
