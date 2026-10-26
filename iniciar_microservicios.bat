@echo off
title Orquestador de Microservicios VetSystem
cd /d "%~dp0"
echo ========================================================
echo       ENCENDIENDO ARQUITECTURA DE MICROSERVICIOS
echo ========================================================
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe microservicios\orchestrator.py
) else (
    python microservicios\orchestrator.py
)
pause
