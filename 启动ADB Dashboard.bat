@echo off
cd /d "%~dp0"
if not exist "node_modules\electron" (
  echo Dependencies are missing. Run npm install first.
  pause
  exit /b 1
)
call npm start
