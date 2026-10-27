# Gates de remediación

Cada lote P0/P1/P2 debe superar los gates aplicables antes de marcar sus tareas como completas.

| Gate | Comando o evidencia | Criterio |
|---|---|---|
| Registro | `python scripts/build_remediation_registry.py` | 29 fixtures, 29 hallazgos y exactamente una prueba de caracterización por `case_id`. |
| Unidad e integración | `python -m pytest -q` | Sin regresiones nuevas; el caso corregido cambia de reproductor a aserción positiva. |
| C17 | `python scripts/check_c_conformance.py --qa-events` | Los 13 harnesses compilan con warnings como error y emiten protocolo válido. |
| Sanitizers | `bash scripts/check_c_sanitizers_linux.sh` | ASan y UBSan sin errores, fugas cubiertas ni comportamiento indefinido. Obligatorio para P0 y cambios C. |
| Reproducción | pruebas de `TraceEngine` y rutas por familia | Avanzar/retroceder/reiniciar conserva estado, línea y consola. |
| UI | suite Playwright configurada en `.github/workflows/e2e-playwright.yml` | DOM por frame coincide con snapshot causal y modo rápido. |
| Generación | `python scripts/run_didactic_generated_audit.py` | 5.000 secuencias deterministas sin divergencias nuevas. |
| OpenSpec | `openspec validate remediate-didactic-c-trace-fidelity --strict` | Cambio válido y tareas/evidencias actualizadas. |

Un gate no puede omitirse por plataforma: si no está disponible localmente queda pendiente y debe
ejecutarse en CI Linux. No se permite cambiar o borrar el oráculo para obtener verde.

