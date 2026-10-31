@echo off
title VetSystem - Detener
cd /d "%~dp0.."
echo Deteniendo instancias de VetSystem...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0detener_sistema.ps1"
timeout /t 2 /nobreak >nul

docker stop vetsystem_gateway >nul 2>&1
docker stop vetsystem_redis >nul 2>&1
