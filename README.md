# Visualizador Web de Estructuras de Datos

Aplicacion web didactica en Flask para practicar TAD con visualizacion interactiva y soporte de codigo C real cuando existe cobertura.

Ultima actualizacion documental: **2026-05-12**.

## Estado actual del proyecto

- Tests: `150 passed, 4 skipped`.
- Cobertura global: `89%` sobre `app/`.
- Entorno verificado: Python `3.10.5` (Windows).

Resultados obtenidos con:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

## Modulos y estructuras

### Secuencial

- Pila (`stack`)
- Cola (`queue`)
- Cola de prioridad (`priority_queue`)
- Lista enlazada (`linked_list`)
- Lista circular (`circular_list`)
- Sublista (`sublist`)

### Jerarquico

- ABB (`abb`)
- AVL (`avl`)
- Rojo-Negro (`red_black`)
- Monticulo binario (`binary_heap`)

### Grafos

- Grafo (`graph`)

### Hash

- Tabla hash (`hash_table`)

## Modo interprete C

Prioriza snippets reales desde `docs/tads_C` para:

- todas las secuenciales,
- todas las jerarquicas,
- grafo.

Comportamiento en UI:

- `Estructura del TAD`: definiciones C.
- `Codigo C: <Operacion>`: funcion C asociada.
- `Historial`: renderizado didactico como `main`.
- `Ejecucion paso a paso`: controles didacticos en este orden:
  - fila superior: `Reproducir` y `Reiniciar`,
  - fila inferior: `Anterior paso` y `Siguiente paso`.

Fallback:

- `app/services/pseudocode_service.py` para estructuras sin cobertura C.
- `hash_table` usa modo didactico/pseudocodigo.

## Reglas de entrada

- Secuencial/Jerarquico: `value`, `parent`, `child` y campos equivalentes se validan como enteros.
- Grafos: `vertex`, `origin`, `target`, `start`, `end` enteros.
- Grafos: `weight` numerico (entero o decimal).
- Hash: `key` y `value` texto.

## Arquitectura

- `app/domain/`: implementaciones de TAD.
- `app/adapters/`: adaptadores con contrato comun.
- `app/services/`: orquestacion, ayuda didactica y estado de sesion.
- `app/routes/`: blueprints Flask por modulo.
- `templates/`: vistas.
- `static/`: CSS/JS de presentacion.
- `tests/`: suite automatizada.

Contrato comun de adapter:

- `create()`
- `execute(operation_name, payload)`
- `to_visual_state()`
- `reset()`
- `get_supported_operations()`

## Endpoints principales

- `GET /` inicio.
- `GET /healthz` health check.
- `GET /assets/<path:filename>` assets de `assets/`.
- `GET /sequential/`, `POST /sequential/<id>/operate`, `POST /sequential/<id>/reset`.
- `GET /hierarchical/`, `POST /hierarchical/<id>/operate`, `POST /hierarchical/<id>/reset`.
- `GET /graph/`, `POST /graph/<id>/operate`, `POST /graph/<id>/reset`.
- `GET /hash/`, `POST /hash/<id>/operate`, `POST /hash/<id>/reset`.
- `GET /help/*` ayudas por modulo y por estructura.

## Ejecucion local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\start_local.bat
```

Abrir en navegador:

```text
http://127.0.0.1:5050/
```

Scripts disponibles:

- `start_local.bat` (recomendado)
- `start_local.ps1`
- `start_5050_verified.bat`
- `run_server_debug.bat`

## Produccion

- Entry point WSGI: `wsgi.py`.
- Servidor sugerido: `waitress`.
- Sesiones server-side con `Flask-Session`.

Variables relevantes:

```text
FLASK_SECRET_KEY=una-clave-segura
FLASK_HOST=127.0.0.1
FLASK_PORT=5050
SESSION_TYPE=cachelib|redis
SESSION_REDIS_URL=redis://host:6379/0
SESSION_COOKIE_SECURE=true|false
SESSION_COOKIE_SAMESITE=Lax
SESSION_LIFETIME_MINUTES=240
SESSION_MAX_HISTORY=300
ENABLE_PROXY_FIX=true
```

Ejecucion de ejemplo:

```powershell
python -m waitress --host=0.0.0.0 --port=5050 wsgi:app
```

## Documentacion relacionada

- [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- [docs/TEST_REPORT.md](docs/TEST_REPORT.md)
- [docs/COVERAGE_DEPRECATION_PLAN.md](docs/COVERAGE_DEPRECATION_PLAN.md)
- `docs/tads_C/` (referencia C)
