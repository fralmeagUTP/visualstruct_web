@echo on
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creando entorno virtual...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No se pudo crear .venv.
    pause
    exit /b 1
  )
)

echo [INFO] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [WARN] Fallo al instalar todas las dependencias.
  echo [WARN] Se intentara iniciar con lo ya instalado en .venv.
  ".venv\Scripts\python.exe" -c "import flask"
  if errorlevel 1 (
    echo [ERROR] Flask no esta instalado y no se puede continuar.
    pause
    exit /b 1
  )
)

set FLASK_HOST=127.0.0.1
set FLASK_PORT=5050

echo [INFO] Iniciando app en http://127.0.0.1:5050
echo [INFO] Deja esta ventana abierta mientras usas la app.
echo.
".venv\Scripts\python.exe" run.py

echo.
echo [ERROR] El servidor se detuvo.
pause
