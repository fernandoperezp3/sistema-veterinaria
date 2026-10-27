@echo off
title VetSystem - Abrir firewall
net session >nul 2>&1
if errorlevel 1 (
    echo Ejecute este archivo con clic derecho ^> Ejecutar como administrador.
    pause
    exit /b 1
)
netsh advfirewall firewall delete rule name="VetSystem HTTPS" >nul 2>&1
netsh advfirewall firewall add rule name="VetSystem HTTPS" dir=in action=allow protocol=TCP localport=80,443 profile=any
echo Listo: puertos 80 y 443 abiertos en redes privadas.
pause
