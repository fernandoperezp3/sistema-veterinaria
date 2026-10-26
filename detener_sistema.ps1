$ruta = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $ruta 'venv'
$procesos = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($venv, [System.StringComparison]::OrdinalIgnoreCase) }
foreach ($p in $procesos) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}
Write-Host ("   Procesos detenidos: " + @($procesos).Count)
