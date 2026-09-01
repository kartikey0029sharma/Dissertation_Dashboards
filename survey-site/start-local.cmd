@echo off
REM Double-click this file to host the study on this computer.
REM It needs Node.js. If the window closes at once, Node is not installed:
REM get it from https://nodejs.org and try again.
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo   Node.js was not found on this computer.
  echo   Install it from https://nodejs.org and run this file again.
  echo.
  pause
  exit /b 1
)
node local-server.js
echo.
echo   The server has stopped.
pause
