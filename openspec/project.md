# Project Context: Visualizador Web de Estructuras de Datos

## Propósito

Aplicación web didáctica en Flask para practicar TADs (Tipos Abstractos de Datos) con
visualización interactiva y un **intérprete gráfico de código C** basado en los TADs
reales ubicados en `docs/tads_C/`.

Versión documentada: **v0.2.5** (2026-05-21).

## Estado verificado del proyecto

- Tests: `285 passed, 0 skipped`.
- Cobertura global: `83%` sobre `app/`.
- Entorno verificado: Python `3.10.5` (Windows).
- Comandos de verificación:
  - `.\.venv\Scripts\python.exe -m pytest -q`
  - `.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing`

## Tech Stack

- **Backend**: Python 3.10, Flask 3.1, Flask-Session 0.8, cachelib, redis (opcional), waitress (producción).
- **Frontend**: HTML (Jinja2), CSS y JavaScript vanilla (sin framework, sin bundler).
- **Testing**: pytest 8.3, Playwright (E2E).
- **Fuente didáctica**: archivos C reales en `docs/tads_C/` (`.c` y `.h`).

## Arquitectura en capas

```
app/
  domain/       # Implementaciones Python de los TADs (réplica semántica de los TADs C)
    sequential/ hierarchical/ graph/ hash/ sorting/
  adapters/     # Adaptadores con contrato común sobre los TADs de dominio
  services/     # Orquestación, código C didáctico, trazas de ejecución, sesión, ayuda
  routes/       # Blueprints Flask por módulo
templates/      # Vistas Jinja2
static/         # CSS/JS de presentación
docs/tads_C/    # Fuente de verdad didáctica en C
tests/          # Suite automatizada
```

Flujo de una operación:

```
POST /<modulo>/<id>/operate
  → SessionService.get_history(id)
  → <Module>StructureService._rebuild_adapter(id, history)   # replay de operaciones mutantes
  → adapter.execute(operation, payload)
  → ExecutionTraceService.build_trace(...)                   # traza didáctica paso a paso
  → SessionService.save_history(id, history)                 # solo si la operación muta
  → JSON {success, message, result?, visual_state, history, execution_trace}
```

## Contrato común de adapters

Todo adapter implementa (`app/adapters/base_adapter.py`):

- `create()`
- `execute(operation_name, payload) -> dict`
- `to_visual_state() -> dict`
- `reset()`
- `get_supported_operations() -> list[dict]` (con flags `mutates`, `inputs`, `hidden`)

## Convenciones de código

- **Idioma**: dominio y mensajes de UI en español; framework/infraestructura en inglés.
- **Type hints** obligatorios con `from __future__ import annotations`.
- **Docstrings** en módulos, clases y funciones públicas.
- Errores de dominio traducidos a mensajes didácticos en la capa de servicios.
- Sin compatibilidad con nombres legacy (`rn_*`, `struct Abb`): la app y la suite están
  alineadas al contrato de los TADs nuevos de `docs/tads_C`.

## Reglas de entrada (validación)

- Secuencial/Jerárquico: `value`, `parent`, `child` y equivalentes se validan como **enteros**.
- Grafos: `vertex`, `origin`, `target`, `start`, `end` **enteros**; `weight` **numérico**.
- Hash: `key` y `value` **texto**.

## Módulos y estructuras soportadas

| Módulo | Estructuras |
|--------|-------------|
| Secuencial | `stack`, `queue`, `priority_queue`, `linked_list`, `circular_list`, `sublist` |
| Jerárquico | `abb`, `avl`, `red_black`, `binary_heap` |
| Grafos | `graph` (4 fases: construcción, recorridos, camino-minimo, expansion-minima) |
| Hash | `hash_table` |
| Ordenamiento | `sorting_array` (11 algoritmos) |

## Decisiones arquitectónicas clave

1. **Estado por replay**: no hay instancias de estructuras en servidor; el estado se
   reconstruye re-ejecutando el historial de operaciones mutantes persistido en sesión.
2. **C real como fuente didáctica**: `CCodeService` extrae funciones y structs de
   `docs/tads_C/`; `PseudocodeService` solo es fallback cuando no hay mapeo C.
3. **Intérprete gráfico, no reproducción lineal**: la traza respeta el flujo de control
   real del código C (solo se animan ramas ejecutadas).
4. **Sesiones server-side** (cachelib filesystem por defecto, Redis opcional).

## Configuración por entorno

Variables relevantes: `FLASK_SECRET_KEY`, `FLASK_HOST`, `FLASK_PORT`,
`SESSION_TYPE` (`cachelib`|`redis`), `SESSION_REDIS_URL`, `SESSION_COOKIE_SECURE`,
`SESSION_COOKIE_SAMESITE`, `SESSION_LIFETIME_MINUTES`, `SESSION_MAX_HISTORY`,
`ENABLE_PROXY_FIX`.

## Testing

- Suite: `tests/` (37 archivos), incluye E2E con Playwright.
- Fixtures Flask en `tests/conftest.py` (`app`, `client`).
- Política: toda operación de adapter, endpoint y traza debe tener cobertura.

## Git

- Ramas: trabajo directo sobre la rama principal del repo local.
- No hacer `commit/push/reset/rebase` sin solicitud explícita del usuario.
