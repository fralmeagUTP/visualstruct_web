# Auditoría generada y regresión

Se ejecutaron secuencias deterministas con semillas reproducibles sobre cinco
familias. Cada secuencia aplica operaciones normales, límites acotados y rutas
de consulta/mutación, verificando el modelo de referencia después de cada paso.

| Familia | Secuencias | Semillas | Fallos nuevos |
|---|---:|---|---:|
| Secuenciales | 1.000 | 810001–811000 | 0 |
| Jerárquicas | 1.000 | 820001–821000 | 0 |
| Grafos | 1.000 | 830001–831000 | 0 |
| Hash | 1.000 | 840001–841000 | 0 |
| Ordenamiento | 1.000 | 850001–851000 | 0 |

Total: **5.000 secuencias**.

Los 29 hallazgos publicados conservan su entrada mínima en el artefacto y tienen
una prueba automatizada cuyo nombre incluye el `case_id`. Se añadió un reductor
`ddmin` determinista para nuevas divergencias y una prueba que demuestra que
reduce una secuencia al disparador mínimo.

El control `product_logic_changes` quedó vacío: esta fase sólo añadió oráculos,
pruebas, scripts y documentación QA; no modificó lógica productiva.

Artefacto reproducible: `docs/qa/generated-audit-v1.json`.
