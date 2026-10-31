@echo off
cd /d "%~dp0.."
if not exist .vscode mkdir .vscode
copy /Y vscode_config\*.json .vscode\ >nul
echo Configuracion de VS Code copiada a .vscode
pause
