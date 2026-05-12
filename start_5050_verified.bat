@echo on
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creando entorno virtual...
  python -m venv .venv
)

echo [INFO] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Fallo al instalar dependencias.
  pause
  exit /b 1
)

set FLASK_HOST=127.0.0.1
set FLASK_PORT=5050

echo [INFO] Cerrando procesos python previos...
powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"

echo [INFO] Iniciando servidor en otra ventana...
start "Flask 5050" cmd /k "cd /d %~dp0 && .\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5050 --no-reload"

echo [INFO] Esperando que el puerto 5050 quede LISTENING...
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 25;$i++){ $line=netstat -ano | Select-String ':5050' | Select-String 'LISTENING'; if($line){ $ok=$true; break }; Start-Sleep -Milliseconds 400 }; if(-not $ok){ exit 1 }"
if errorlevel 1 (
  echo [ERROR] El servidor no quedo escuchando en 5050.
  echo [ERROR] Revisa la ventana 'Flask 5050' para ver el traceback.
  pause
  exit /b 1
)

echo [INFO] Servidor activo. Abriendo navegador...
start "" "http://127.0.0.1:5050/hierarchical/"
echo [OK] Si no carga, revisa la ventana 'Flask 5050'.
pause
