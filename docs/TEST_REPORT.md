# Informe de Testeo Integral

Fecha: **18 de mayo de 2026**  
Proyecto: `Web_VisualEstruct`

## 1. Objetivo

Validar de forma integral la calidad funcional, tecnica y de regresion de la app:

- dominio y adaptadores por modulo,
- rutas Flask y contratos de API,
- motor de interpretacion y simulacion visual,
- consistencia con TAD nuevos en `docs/tads_C`,
- pruebas E2E de interfaz.

## 2. Ejecuciones realizadas

1. Suite completa:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado: **274 passed**.

2. Suite con cobertura:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

Resultado: **274 passed**, cobertura global **85%**.

## 3. Resumen global

- Items recolectados: `274`
- Exitosos: `274`
- Fallidos: `0`
- Omitidos: `0`
- Cobertura total (`app/`): **85%** (`8697` lineas, `1307` no cubiertas)

Incluye `tests/test_ui_playwright_e2e.py` ejecutado y aprobado en la corrida integral.

## 4. Cobertura por areas (observacion ejecutiva)

### Cobertura alta (>= 90%)

- Inicializacion app y rutas base: `app/__init__.py` `100%`, `app/routes/main_routes.py` `100%`
- Servicios clave:
  - `app/services/structure_service.py` `100%`
  - `app/services/c_code_service.py` `90%`
  - `app/services/graph_help_service.py` `100%`
- Adaptadores:
  - `app/adapters/graph_adapter.py` `93%`
  - `app/adapters/hash_table_adapter.py` `94%`
  - `app/adapters/priority_queue_adapter.py` `100%`
- Wrappers de dominio:
  - `app/domain/sequential/tad_wrappers.py` `89%` (frontera alta-media)
  - `app/domain/graph/tad_wrappers.py` `97%`
  - `app/domain/hierarchical/tad_wrappers.py` `93%`

### Cobertura media (70% a 89%)

- Rutas:
  - `app/routes/sequential_routes.py` `87%`
  - `app/routes/graph_routes.py` `84%`
  - `app/routes/hash_routes.py` `83%`
  - `app/routes/hierarchical_routes.py` `71%`
- Servicios:
  - `app/services/graph_structure_service.py` `87%`
  - `app/services/hierarchical_structure_service.py` `82%`
- TAD jerarquicos puntuales:
  - `app/domain/hierarchical/tad_abb.py` `75%`
  - `app/domain/hierarchical/tad_avl.py` `70%`

### Cobertura baja (< 70%)

- `app/domain/graph/tad_grafo.py`: `49%`
- `app/domain/hash/tad_tabla_hash.py`: `59%`
- `app/domain/hierarchical/tad_monticulo_binario.py`: `59%`
- `app/services/pseudocode_service.py`: `67%`

## 5. Verificacion funcional destacada

- Interpretacion paso a paso validada en modulos secuencial, jerarquico, grafos y hash.
- Modo rapido validado:
  - checkbox desactivado aplica resultado final.
  - en grafos, el resultado visual final coincide con el ultimo estado de la traza (recorrido/camino/MST).
- Ayuda y contenidos C validados con pruebas de soporte (`test_help_c_content.py`).
- Migracion a TAD nuevos verificada por pruebas de remocion legacy:
  - secuencial, jerarquico, grafos y hash.

## 6. Riesgos tecnicos pendientes

1. Cobertura baja en implementaciones de dominio puro (`tad_grafo.py`, `tad_tabla_hash.py`, `tad_monticulo_binario.py` jerarquico).
2. `pseudocode_service.py` mantiene rutas de fallback no ejercitadas completamente.
3. Rutas de error menos frecuentes en `hierarchical_routes.py` y `graph_routes.py` aun con margen de mejora.

## 7. Recomendaciones inmediatas

1. Agregar pruebas unitarias directas de dominio para `app/domain/graph/tad_grafo.py` cubriendo mas ramas de errores y casos extremos.
2. Ampliar pruebas de hash de bajo nivel para colisiones, redimensionamiento y borrados encadenados en `tad_tabla_hash.py`.
3. Incorporar pruebas especificas de rutas de fallo (payload invalido, ids inexistentes) para subir cobertura de blueprints.
4. Mantener la corrida E2E de Playwright en CI para proteger regresiones de UX en modo rapido/paso a paso.

## 8. Comandos de reproduccion

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

Opcional (solo UI E2E):

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_ui_playwright_e2e.py -q
```

## 9. Veredicto

El estado actual es **estable y consistente** con los TAD nuevos: la suite completa pasa (`274/274`) y la cobertura global sube a `85%`.  
Queda trabajo puntual de cobertura en implementaciones de dominio de grafos/hash/monticulo jerarquico y en rutas de error menos frecuentes.
