@echo off
title VetSystem - Lanzador del Sistema Completo
cd /d "%~dp0"
echo ======================================================================
echo          VETSYSTEM - SISTEMA VETERINARIO ^& MICROSERVICIOS
echo ======================================================================

set "PY=python"
if exist venv\Scripts\python.exe set "PY=venv\Scripts\python.exe"

echo [1/5] Cerrando instancias anteriores...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0detener_sistema.ps1"
timeout /t 2 /nobreak >nul

echo [2/5] Verificando base de datos MySQL...
%PY% esperar_bd.py 5 >nul 2>&1
if errorlevel 1 (
    docker inspect vetsystem_mysql >nul 2>&1
    if not errorlevel 1 (
        echo    MySQL no responde. Reiniciando contenedor vetsystem_mysql...
        docker restart vetsystem_mysql >nul
    )
)
%PY% esperar_bd.py 90
if errorlevel 1 (
    echo.
    echo    No se pudo conectar a MySQL. Encienda MySQL ^(Docker Desktop o XAMPP^) y vuelva a intentar.
    pause
    exit /b 1
)

echo [3/5] Aplicando migraciones pendientes...
%PY% manage.py migrate --noinput
if errorlevel 1 (
    echo    Error al aplicar migraciones.
    pause
    exit /b 1
)

echo [4/5] Iniciando los 4 Microservicios (Puertos 8081, 8082, 8083, 8084)...
start "VetSystem - Microservicios" cmd /k "iniciar_microservicios.bat"
timeout /t 3 /nobreak >nul

echo [5/5] Abriendo el navegador en http://127.0.0.1:8080/ ...
set "BRAVE=%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"
if not exist "%BRAVE%" set "BRAVE=%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"
if exist "%BRAVE%" (
    start "" "%BRAVE%" http://127.0.0.1:8080/
) else (
    start http://127.0.0.1:8080/
)

echo.
echo ======================================================================
echo    INICIANDO SERVIDOR WEB PRINCIPAL (DJANGO EN PUERTO 8080)
echo ======================================================================
%PY% manage.py runserver 0.0.0.0:8080
pause
