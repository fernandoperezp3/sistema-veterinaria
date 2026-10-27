@echo off
title VetSystem - Lanzador del Sistema Completo
cd /d "%~dp0"
echo ======================================================================
echo          VETSYSTEM - SISTEMA VETERINARIO ^& MICROSERVICIOS
echo ======================================================================

set "PY=python"
if exist venv\Scripts\python.exe set "PY=venv\Scripts\python.exe"

echo [1/6] Cerrando instancias anteriores...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0detener_sistema.ps1"
timeout /t 2 /nobreak >nul

echo [2/6] Verificando base de datos MySQL...
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

echo    Iniciando Redis ^(cache de sesiones y dashboard^)...
docker start vetsystem_redis >nul 2>&1 || docker run -d --name vetsystem_redis --restart unless-stopped -p 6379:6379 redis:7-alpine >nul 2>&1
%PY% -c "import redis" >nul 2>&1 || %PY% -m pip install -q "redis>=5.0"

echo [3/6] Aplicando migraciones pendientes...
%PY% manage.py migrate --noinput
if errorlevel 1 (
    echo    Error al aplicar migraciones.
    pause
    exit /b 1
)
%PY% manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete(); from django.core.cache import cache; cache.clear()" >nul 2>&1

echo [4/6] Iniciando los 4 Microservicios (Puertos 8081, 8082, 8083, 8084)...
start "VetSystem - Microservicios" cmd /k "iniciar_microservicios.bat"
timeout /t 3 /nobreak >nul

echo [5/6] Iniciando gateway Nginx HTTPS (puertos 80 y 443)...
docker rm -f vetsystem_gateway >nul 2>&1
docker run -d --name vetsystem_gateway --restart unless-stopped -p 80:80 -p 443:443 --add-host=host.docker.internal:host-gateway -v "%~dp0nginx\lan.conf:/etc/nginx/conf.d/default.conf:ro" -v "%~dp0nginx\certs:/etc/nginx/certs:ro" nginx:alpine >nul
if errorlevel 1 (
    echo    No se pudo iniciar Nginx. Verifique que Docker Desktop este abierto.
    set "URL=http://127.0.0.1:8080/login/"
) else (
    set "URL=https://localhost/login/"
)

for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -and $_.NetAdapter.Status -eq 'Up' } | Select-Object -First 1).IPv4Address.IPAddress"`) do set "IPLAN=%%i"

echo [6/6] Abriendo el navegador en %URL% ...
set "BRAVE=%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"
if not exist "%BRAVE%" set "BRAVE=%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"
if exist "%BRAVE%" (
    start "" "%BRAVE%" %URL%
) else (
    start %URL%
)

echo.
echo ======================================================================
echo    ACCESO LOCAL:          %URL%
echo    DESDE OTRA PC (RED):   https://%IPLAN%.nip.io/login/
echo    (sin internet usar:    https://%IPLAN%/login/ - sin login de Google)
echo    (Aceptar la advertencia del certificado: Avanzado ^> Continuar)
echo ======================================================================
echo    INICIANDO SERVIDOR WEB PRINCIPAL (DJANGO EN PUERTO 8080)
echo ======================================================================
%PY% manage.py runserver 0.0.0.0:8080
pause
