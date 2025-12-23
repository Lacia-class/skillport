@echo off
setlocal
setx SKILLPORT_EMBEDDING_PROVIDER "dashscope" >nul
setx SKILLPORT_EMBEDDING_BASE_URL "https://dashscope.aliyuncs.com/compatible-mode/v1" >nul
setx SKILLPORT_EMBEDDING_MODEL "text-embedding-v3" >nul
echo Switched embedding to DASHSCOPE (text-embedding-v3).
echo Note: restart terminals/IDEs to pick up new env vars.
echo API key must be set in DASHSCOPE_API_KEY.
pause
