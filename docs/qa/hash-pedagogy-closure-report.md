# Informe de cierre pedagógico y QA del módulo de tablas hash

## Resultado

El módulo interpreta el TAD C de capacidad fija con claves y valores `int`. Cada frame vincula la línea C ejecutada con bucket, cadena, punteros, memoria, invariante y costo observado.

## Antes y después

| Área | Antes | Después |
|---|---|---|
| Contrato | Valores textuales y afirmaciones de resize | `int`/`int`, capacidad fija y sin rehash ficticio |
| Hash | Bucket mostrado sin residuo C explícito | Residuo, normalización, bucket final y límites de `int` |
| Colisiones | Cadena estática | Nodos con dirección lógica, campos, `siguiente` y `NULL` |
| Búsqueda/eliminación | Flujo genérico | Recorrido causal de `actual`/`anterior`, ramas correctas, enlace y `free` |
| Ciclo de vida | Limpiar y destruir poco diferenciados | Liberación individual, arreglo de buckets, `NULL` y capacidad/cantidad cero |
| Aprendizaje | Casos aislados | Ejemplos, predicción, pistas, práctica y progreso de sesión |
| Comparación | No disponible | Capacidades 3/7/17 sobre copias aisladas y entrada inmutable |
| Cierre | Sin exportación específica | Captura JPG, resumen JSON, ayuda, glosario y guía docente |

## Evidencia

- 902 pruebas no-E2E aprobadas con cobertura; los gates de cobertura global y componentes críticos aprobaron.
- Contratos, golden traces, conformance C/Python, propiedades de límite y equivalencia rápido/paso a paso: automatizados.
- Playwright del hash cubre reproducción, práctica, comparación, teclado, responsividad y exportación.
- El `main` representativo generado por el historial y el harness C17 de hash se compilan con `-Wall -Wextra -Wpedantic -Werror`; el harness se ejecuta con eventos QA.
- ASan/UBSan se intentó en Windows; el GCC MinGW local no dispone de `libasan` ni `libubsan`. El workflow Linux permanece como gate obligatorio de sanitizers.

## Riesgo residual

La evidencia de sanitizers debe confirmarse en CI Linux. La comparación de capacidades es demostrativa: una entrada concreta no demuestra la complejidad promedio universal.
