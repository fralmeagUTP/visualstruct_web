# Tutorial completo: despliegue en cPanel (Python App + FTP)

Este tutorial explica, paso por paso, como publicar esta app Flask en un hosting con cPanel.

Escenario recomendado en este proyecto:
- Dominio: `nyquist.app`
- Subruta publica: `/visualstruct`
- App root en servidor: `/home/ur5cxigur1qs/visualstruct`
- Startup file: `wsgi.py`
- Entry point: `app`

> Nota: Puedes cambiar rutas y dominio, pero manteniendo la misma logica.

---

## 1) Requisitos previos

Antes de configurar cPanel, confirma que tienes:

1. Acceso a cPanel.
2. Acceso a File Manager o FTP/SFTP.
3. Codigo fuente completo del proyecto.
4. Archivo `requirements.txt` actualizado.
5. Archivo `wsgi.py` en la raiz del proyecto con:

```python
from app import create_app

app = create_app()
```

---

## 2) Estructura esperada en tu proyecto

En local, el proyecto debe contener como minimo:

- `wsgi.py`
- `requirements.txt`
- `app/`
- `templates/`
- `static/`

Adicionalmente puede tener otros archivos, pero esos son los criticos para el arranque web.

---

## 3) Que subir por FTP/SFTP (y que NO subir)

### Subir SI

Sube al servidor estos elementos del proyecto:

- `wsgi.py`
- `run.py` (opcional para debug, no critico para cPanel)
- `requirements.txt`
- Carpeta `app/`
- Carpeta `templates/`
- Carpeta `static/`
- Carpeta `assets/` (si tu app la usa)

### Subir NO (o no es necesario)

No subas estas carpetas/archivos de desarrollo:

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `coverage_html/`
- `tests/` (opcional en produccion)
- `.git/`
- Archivos temporales de log local

---

## 4) Carpeta destino en servidor

Para evitar conflictos, usa una carpeta unica para la app:

- Recomendado: `/home/ur5cxigur1qs/visualstruct`

Si ya habias subido en `public_html/visualstruct`, puedes mover/copyar al path recomendado y apuntar cPanel a ese nuevo root.

---

## 5) Crear o editar Python App en cPanel

En cPanel:

1. Ir a **Software > Python App** (o Applications > Python).
2. Crear aplicacion nueva o editar la existente.
3. Completar campos:

- Python version: `3.10.x`
- Application root: `visualstruct`
- Application URL:
  - Dominio: `nyquist.app`
  - Ruta: `visualstruct`
- Application startup file: `wsgi.py`
- Application Entry point: `app`
- Passenger log file: `/home/ur5cxigur1qs/logs/visualstruct_passenger.log`

4. Guardar cambios.

---

## 6) Entender el Entry point (muy importante)

El Entry point se toma del nombre de variable en el startup file.

En `wsgi.py`:

```python
app = create_app()
```

Por lo tanto:

- Startup file = `wsgi.py`
- Entry point = `app`

Si cambias la variable por otro nombre (ejemplo `mi_app = create_app()`), entonces el Entry point debe ser `mi_app`.

---

## 7) Instalar dependencias en cPanel

Con la app guardada:

1. En la seccion **Configuration files**, agrega `requirements.txt`.
2. Presiona **Run Pip Install**.
3. Espera finalizacion completa.

Opcional por terminal (si tu hosting lo permite):

```bash
source /home/ur5cxigur1qs/virtualenv/visualstruct/3.10/bin/activate
pip install --upgrade pip
pip install -r /home/ur5cxigur1qs/visualstruct/requirements.txt
```

---

## 8) Variables de entorno recomendadas

En cPanel, agrega estas variables en la Python App:

- `APP_ENV` = `production`
- `FLASK_SECRET_KEY` = clave larga y aleatoria
- `SESSION_COOKIE_SECURE` = `true`
- `ENABLE_PROXY_FIX` = `true`
- `TRUSTED_PROXY_COUNT` = cantidad exacta de proxies confiables (normalmente `1`, confirmar con el proveedor)
- `SESSION_TYPE` = `cachelib`
- `SESSION_CACHE_DIR` = `/home/ur5cxigur1qs/visualstruct/.flask_session`
- `SESSION_COOKIE_SAMESITE` = `Lax`

Generar clave segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

No reutilices `dev-secret-key-change-me`: la aplicacion rechaza esa clave cuando
`APP_ENV=production`. Tampoco habilites `ENABLE_PROXY_FIX` sin `TRUSTED_PROXY_COUNT`, porque
confiar saltos de mas permite falsificar headers `X-Forwarded-*`. Si cPanel no termina HTTPS,
revisa la topologia antes de cambiar `SESSION_COOKIE_SECURE`; el override
`ALLOW_INSECURE_COOKIES_IN_PRODUCTION=true` debe limitarse a una red HTTP controlada.

Configuracion opcional de checkpoints (desactivada inicialmente):

- `ENABLE_CHECKPOINTS` = `false`
- `CHECKPOINT_INTERVAL` = `50`
- `CHECKPOINT_MAX_PER_STRUCTURE` = `1`

---

## 9) Reiniciar y validar

1. Pulsar **Restart** en la Python App.
2. Probar ruta de salud:

- `https://nyquist.app/visualstruct/healthz`

Respuesta esperada de esta app:

```json
{"status": "ok"}
```

3. Probar home:

- `https://nyquist.app/visualstruct/`

---

## 10) Como detectar si cPanel esta cargando la app incorrecta

Si ves en navegador:

- `It works!`
- `Python v3.x.x`

Eso normalmente indica pagina de prueba/default de Passenger, no tu Flask real.

Revisa en ese caso:

1. El codigo realmente esta en el `Application root` configurado.
2. Existe `wsgi.py` dentro de ese root.
3. Startup file y Entry point coinciden exactamente.
4. Ejecutaste `Run Pip Install` en la app correcta.
5. Reiniciaste despues de cambios.

---

## 11) Flujo de recuperacion rapida (si se desconfigura)

1. Confirmar carpeta real del codigo:
   - `/home/ur5cxigur1qs/visualstruct`
2. Corregir App Root en cPanel.
3. Verificar startup (`wsgi.py`) y entry (`app`).
4. Ejecutar `Run Pip Install`.
5. Reiniciar.
6. Validar `/visualstruct/healthz`.
7. Si falla, revisar log de Passenger.

---

## 12) Log y troubleshooting

Log definido:

- `/home/ur5cxigur1qs/logs/visualstruct_passenger.log`

Errores tipicos:

1. `ModuleNotFoundError`
   - Causa: dependencia no instalada.
   - Solucion: correr `Run Pip Install` y reiniciar.

2. `No such application`
   - Causa: app root invalido o app corrupta.
   - Solucion: editar root o recrear app con mismo URI y root correcto.

3. 404 en assets/CSS/JS
   - Causa: rutas absolutas no compatibles con subruta `/visualstruct`.
   - Solucion: usar rutas con `url_for` y rutas relativas correctas.

---

## 13) Checklist final

Marca cada punto antes de dar por terminado:

- [ ] Codigo subido al root correcto.
- [ ] `wsgi.py` presente en root.
- [ ] Startup file = `wsgi.py`.
- [ ] Entry point = `app`.
- [ ] `requirements.txt` instalado.
- [ ] Variables de entorno configuradas.
- [ ] App reiniciada.
- [ ] `healthz` responde JSON `{"status":"ok"}`.
- [ ] Home carga sin errores de CSS/JS.

---

## 14) Comandos de referencia rapida

Copiar proyecto (SSH):

```bash
mkdir -p /home/ur5cxigur1qs/visualstruct
cp -a /home/ur5cxigur1qs/public_html/visualstruct/. /home/ur5cxigur1qs/visualstruct/
```

Limpiar basura de desarrollo:

```bash
rm -rf /home/ur5cxigur1qs/visualstruct/.venv
rm -rf /home/ur5cxigur1qs/visualstruct/__pycache__
rm -rf /home/ur5cxigur1qs/visualstruct/.pytest_cache
```

Reiniciar app desde UI de cPanel y validar:

```text
https://nyquist.app/visualstruct/healthz
```

---

Fin del tutorial.
