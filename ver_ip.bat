@echo off
cd /d "%~dp0"
ipconfig > _ip.txt 2>&1
netsh advfirewall firewall show rule name="VetSystem HTTPS" >> _ip.txt 2>&1
powershell -NoProfile -Command "Get-NetConnectionProfile | Format-Table -AutoSize Name,InterfaceAlias,NetworkCategory" >> _ip.txt 2>&1
echo listo > _ip_fin.txt
