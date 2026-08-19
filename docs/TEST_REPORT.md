# Informe de pruebas y calidad

Fecha: **19 de agosto de 2026**
Proyecto: `Web_VisualEstruct`
Entorno local de referencia: Python `3.10.5`, Windows 10.

## 1. Resultado funcional

La regresión completa, incluyendo las nueve pruebas E2E con Chromium, finalizó con:

```text
530 passed
```

Comando reproducible:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas E2E también pueden ejecutarse en su job independiente:

```powershell
.\.venv\Scripts\playwright.exe install chromium
.\.venv\Scripts\python.exe -m pytest -q -m e2e
```

El workflow `.github/workflows/e2e-playwright.yml` instala el navegador y sus dependencias en Linux.

## 2. Cobertura y gates

La medicion instrumentada, excluyendo E2E y pruebas temporizadas, obtuvo:

```text
518 passed, 11 deselected
Cobertura global: 89%
```

Los gates vigentes son:

| Componente | Medido | Minimo |
|---|---:|---:|
| Global `app/` | 89% | 83% |
| `domain/sorting/tad_ordenamiento.py` | 100% | 85% |
| `domain/graph/tad_grafo.py` | 100% | 85% |
| `domain/hash/tad_tabla_hash.py` | 99% | 85% |
| `domain/hierarchical/tad_monticulo_binario.py` | 99% | 85% |

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not e2e and not performance" --cov=app --cov-report=term-missing --cov-report=json:coverage.json
.\.venv\Scripts\python.exe scripts\check_coverage_gates.py --report coverage.json
```

El verificador falla si baja la cobertura global, un componente critico queda bajo 85% o falta
del reporte.

## 3. Conformidad C y seguridad de memoria

Existen harnesses no interactivos para los 13 TAD. La conformidad estricta compila con C17,
warnings como error y compara estados canonicos C/Python.

```powershell
.\.venv\Scripts\python.exe scripts\check_c_conformance.py
```

La CI Linux mantiene dos jobs independientes:

- `c17-conformance`: compilacion y escenarios diferenciales estrictos.
- `sanitizers`: AddressSanitizer y UndefinedBehaviorSanitizer.

Los 13 harnesses pasaron C17 estricto en Windows. En Linux sobre Docker se ejecutaron, para cada
TAD, pases independientes de AddressSanitizer y UndefinedBehaviorSanitizer sin diagnósticos. Los
pases separados evitan una interferencia observada entre ambos runtimes bajo Docker Desktop.

La campaña diferencial reproducible ejecutó 1.000 secuencias por cada una de las cinco familias
(5.000 en total, semilla base `20260819`, longitud 5) y obtuvo cero divergencias. Reporte:
`docs/differential_campaign_5000.json`.

## 4. Checkpoints y rendimiento

Se verificaron formato versionado, SHA-256 determinista, compatibilidad, corrupcion, truncado,
offset invalido, importacion parcial y fallback a replay completo. Las sesiones antiguas con una
lista de operaciones se migran a un registro versionado sin perder eventos.

Benchmark de reconstruccion, 20 iteraciones y 300 operaciones por familia:

| Familia | p95 |
|---|---:|
| Secuencial | 1.349 ms |
| Arboles | 45.109 ms |
| Grafos | 23.900 ms |
| Hash | 47.882 ms |
| Ordenamiento | 1.637 ms |

Todas cumplen el presupuesto p95 menor a `200 ms`. La medicion usa checkpoint ausente y replay
completo, el peor caso seguro. Reporte: `docs/checkpoint_reconstruction_benchmark.json`.

## 5. Configuracion y observabilidad

El arranque valida `APP_ENV`, host, puerto, sesiones, cookies, checkpoints y proxies. En
produccion rechaza la clave de desarrollo, cookies inseguras sin override explicito, DEBUG/TESTING
y ProxyFix sin conteo de saltos confiables.

El logger `visualstruct.operations` emite JSON para:

- validacion de trazas: duracion, estrategia y cantidad de pasos;
- replay: duracion, operaciones recibidas y operaciones validas;
- reconstruccion: uso/fallback de checkpoint, motivo categorico y operaciones pendientes.

Las pruebas verifican que estos eventos no contienen estados, historiales, cookies, secretos ni
payloads de usuario.

## 6. Topologia de CI

| Job | Responsabilidad |
|---|---|
| `unit-integration` | Suite Python y gates de cobertura |
| `e2e` | Interfaz real con Chromium/Playwright |
| `c17-conformance` | Los 13 harnesses y conformidad C17 |
| `sanitizers` | ASan y UBSan en Linux |

Pruebas estaticas protegen la separacion de jobs y sus comandos criticos.

## 7. Veredicto

El incremento `harden-trace-conformance-and-state` mantiene la regresión Python en verde,
eleva los cuatro componentes criticos sobre su gate, agrega conformidad C reproducible y endurece
configuración, checkpoints y observabilidad. La fase 7 queda verificada: suite completa con
Chromium, cobertura, 5.000 secuencias diferenciales, 13 TAD con C17/ASan/UBSan, migración de
sesiones anteriores a checkpoints y validación estricta de OpenSpec.
