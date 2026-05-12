# Informe de Testeo Integral

Fecha: **12 de mayo de 2026**  
Proyecto: `Web_VisualEstruct`

## 1. Objetivo

Validar el estado funcional y tecnico de la aplicacion:

- pruebas unitarias de dominio y adapters,
- pruebas de rutas Flask,
- pruebas de coherencia historial/estado visual,
- cobertura de codigo,
- pruebas E2E opcionales con Playwright.

## 2. Ejecuciones realizadas

1. Suite completa:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Resultado: **150 passed, 4 skipped**.

2. Suite con cobertura:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

Resultado: **150 passed, 4 skipped**, cobertura total **89%**.

## 3. Resumen de cobertura

- Lineas totales analizadas: `4899`
- Lineas no cubiertas: `518`
- Cobertura global: `89%`

Archivos con cobertura destacada:

- `app/__init__.py`: `100%`
- `app/services/structure_service.py`: `100%`
- `app/adapters/priority_queue_adapter.py`: `100%`
- `app/domain/graph/grafo.py`: `94%`
- `app/domain/hierarchical/abb.py`: `97%`
- `app/domain/hash/tabla_hash.py`: `96%`

Archivos con mayor oportunidad de mejora:

- `app/domain/hash/lista_enlazada.py`: `68%`
- `app/routes/hierarchical_routes.py`: `71%`
- `app/routes/main_routes.py`: `73%`
- `app/services/pseudocode_service.py`: `67%`
- `app/services/hierarchical_structure_service.py`: `74%`

## 4. Estado de la suite

- Total de items recolectados: `154`
- Tests omitidos: `4` (Playwright E2E condicional)
- Meta de cobertura historica (`>=88%`): **cumplida**

## 5. Verificacion UI paso a paso

Se verifico que los modulos `sequential`, `hierarchical`, `hash` y `graph` renderizan los controles actuales:

- `Reproducir`
- `Reiniciar`
- `Anterior paso`
- `Siguiente paso`
- texto `Ejecucion paso a paso`

## 6. Comandos de reproduccion

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

Comandos opcionales para E2E:

```powershell
pip install playwright
python -m playwright install chromium
.\.venv\Scripts\python.exe -m pytest tests\test_ui_playwright_e2e.py -q
```

## 7. Veredicto

El estado actual es **estable**: toda la suite funcional pasa, la cobertura global se mantiene en `89%` (por encima de la meta `>=88%`) y no se observaron regresiones en los flujos principales.
