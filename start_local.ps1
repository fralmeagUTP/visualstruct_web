Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

try {
    $python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $python)) {
        Write-Host "No existe .venv. Creando entorno virtual..." -ForegroundColor Yellow
        python -m venv .venv
    }

    Write-Host "Instalando dependencias..." -ForegroundColor Cyan
    & $python -m pip install -r requirements.txt | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Aviso: no se pudieron instalar todas las dependencias." -ForegroundColor Yellow
        Write-Host "Se intentara iniciar con lo ya instalado en .venv." -ForegroundColor Yellow
        & $python -c "import flask"
        if ($LASTEXITCODE -ne 0) {
            throw "Flask no esta instalado y no se puede iniciar."
        }
    }

    $env:FLASK_HOST = "127.0.0.1"
    $env:FLASK_PORT = "5050"

    Write-Host "Verificando puerto 5050 antes de iniciar..." -ForegroundColor Cyan
    netstat -ano | Select-String ":5050" | Out-Host

    Write-Host "Iniciando servidor en http://127.0.0.1:5050" -ForegroundColor Green
    Write-Host "Manten esta ventana abierta mientras usas la app." -ForegroundColor Green
    Write-Host ""

    & $python run.py
}
catch {
    Write-Host ""
    Write-Host "[ERROR] No fue posible iniciar el servidor." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
