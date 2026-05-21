# Visualizador Web de Estructuras de Datos

Aplicacion web didactica en Flask para practicar TAD con visualizacion interactiva y modo interprete de codigo C basado en los TAD nuevos de `docs/tads_C`.

Version actual: **v0.2.5**  
Ultima actualizacion documental: **2026-05-21**.

## Estado actual del proyecto

- Tests: `285 passed, 0 skipped`.
- Cobertura global: `83%` sobre `app/` (ejecucion sin exclusiones).
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

### Ordenamiento

- Arreglo de ordenamiento (`sorting_array`)

## Modo interprete C

Prioriza snippets reales desde `docs/tads_C` para:

- todas las secuenciales,
- todas las jerarquicas,
- grafo,
- hash (`hash_table`),
- ordenamiento (`sorting_array`).

Comportamiento en UI:

- `Estructura del TAD`: definiciones C.
- `Codigo C: <Operacion>`: funcion C asociada.
- `Historial`: renderizado didactico como `main`.
- `Ejecucion paso a paso`:
  - secuencial/jerarquico/hash: controles en este orden:
  - fila superior: `Reproducir` y `Reiniciar`,
  - fila inferior: `Anterior paso` y `Siguiente paso`.
  - grafo: la simulacion esta en `Paso 3` con `Reproducir`, `Anterior paso` y `Siguiente paso`.
  - grafo: `Siguiente paso` avanza linea a linea y `Accion actual` clasifica el paso (`Evaluando condicion` o `Aplicando cambio`).
  - todos los modulos: checkbox `Interpretar codigo paso a paso`:
    - activado: reproduce la traza completa.
    - desactivado: aplica solo el resultado final.
    - cuando esta desactivado, `Anterior paso` y `Siguiente paso` quedan deshabilitados.
  - consola C e historial tecnico:
    - se evita repetir mensajes consecutivos equivalentes para reducir redundancia visual.
  - en estructuras secuenciales, al finalizar la simulacion queda visible solo la estructura final
    (sin bloques temporales `aux`).
  - grafo en modo rapido: el resultado final visual debe ser equivalente al ultimo paso del modo interpretado
    (mismos nodos/aristas resaltados para recorrido, camino minimo o MST).
  - grafo en modo rapido: se ocultan controles de navegacion por paso (`Anterior`, `Siguiente`, velocidad, contador y accion actual).
  - el control global `Mostrar codigo y detalles tecnicos` se ubica en la misma fila del menu superior.
  - boton global `Exportar JPG` en la misma fila del menu superior para descargar el estado visual actual.
  - el exportador permite elegir `Calidad` (`Media`, `Alta`, `Maxima`) y `Escala` (`1x`, `2x`, `3x`).

Fallback:

- `app/services/pseudocode_service.py` queda como respaldo didactico cuando no existe mapeo C para una operacion puntual.

Compatibilidad:

- La app y la suite estan alineadas al contrato de los TAD nuevos (sin compatibilidad con nombres legacy como `rn_*` o `struct Abb`).

## Especificacion didactica de simulacion visual

La app debe comportarse como un **interprete grafico de codigo C** y no como una reproduccion lineal de lineas.

Criterios obligatorios:

- La simulacion debe respetar el flujo de control real del codigo C (`if`, `else`, `while`, `for`, `switch`): solo se animan ramas ejecutadas.
- Cada operacion mutante debe mostrar fases visuales del metodo:
  - estado inicial,
  - creacion de estructura temporal (por ejemplo `aux`),
  - enlace/asignacion intermedia (por ejemplo `aux->sgte = ...`),
  - reasignacion a la estructura original (por ejemplo `*p = aux`),
  - estado final confirmado.
- Cuando el metodo use nodos o punteros temporales, estos deben renderizarse en un bloque separado y con etiquetas de paso.
- El resaltado del codigo C debe avanzar sincronizado con la animacion del estado.
- La consola `printf` debe reflejar las salidas efectivamente ejecutadas en la ruta de control actual.
- La consola `printf` y el historial tecnico deben minimizar mensajes redundantes consecutivos.
- El historial en `main` debe mantenerse coherente con la ejecucion y con el estado visual final.
- Esta especificacion aplica a todos los modulos y solo sobre TAD nuevos de `docs/tads_C`.

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
- `GET /graph/<id>/<phase>` para fases del modulo de grafos (`construccion`, `recorridos`, `camino-minimo`, `expansion-minima`).
- `GET /hash/`, `POST /hash/<id>/operate`, `POST /hash/<id>/reset`.
- `GET /sorting/`, `GET /sorting/visualizador`.
- `POST /api/ordenamiento/create-array`, `/random-array`, `/algorithm`, `/run`, `/step`, `/reset`.
- `GET /api/ordenamiento/state`.
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
- Manual didactico en la app: `GET /help/manual`
