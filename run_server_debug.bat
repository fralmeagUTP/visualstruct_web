@echo on
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creando entorno virtual...
  python -m venv .venv
)

echo [INFO] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Fallo instalando dependencias.
  pause
  exit /b 1
)

set FLASK_HOST=127.0.0.1
set FLASK_PORT=5050

echo [INFO] Verificando puerto 5050 antes de iniciar...
netstat -ano | findstr :5050

echo [INFO] Iniciando app en http://127.0.0.1:5050
echo [INFO] Esta ventana debe quedarse abierta.
".venv\Scripts\python.exe" -m flask --app app run --host %FLASK_HOST% --port %FLASK_PORT% --no-reload

echo [ERROR] El servidor se detuvo. Revisa mensajes anteriores.
pause
