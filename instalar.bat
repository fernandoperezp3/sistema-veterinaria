@echo off
title VetSystem - Instalacion
cd /d "%~dp0"
echo ======================================================================
echo          VETSYSTEM - INSTALACION DE DEPENDENCIAS
echo ======================================================================
if not exist venv\Scripts\python.exe (
    echo [1/4] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo No se pudo crear el entorno virtual. Verifique que Python este instalado y en el PATH.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Entorno virtual encontrado.
)
echo [2/4] Actualizando pip...
venv\Scripts\python.exe -m pip install --upgrade pip
echo [3/4] Instalando librerias...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error instalando dependencias.
    pause
    exit /b 1
)
echo [4/4] Aplicando migraciones (MySQL debe estar encendido)...
venv\Scripts\python.exe manage.py migrate
echo.
echo Instalacion terminada. Ejecute iniciar_sistema_completo.bat
pause
