# Entrega local — reparación pedagógica VisualStruct

## Resultado de la revisión definida
La copia aislada queda verificada en las cinco familias, en el orden solicitado. Matriz UI: **95 acciones/operaciones PASS_UI y14 NOT_EXPOSED**; ordenamiento incluye11algoritmos desglosados. De las95filas,94 tienen paso a paso y una es preparación sin traza propia. Se corrigieron los defectos encontrados de ejecución, navegación, explicación, código visible, memoria, resultados, reset y exportación. No se afirma exhaustividad universal.

- Ordenamiento:11algoritmos y6acciones.
- Secuenciales:29operaciones de6estructuras.
- Jerárquicas:33operaciones de4estructuras.
- Grafos:16acciones visibles en4fases.
- Hash:11operaciones; límite educativo128 y conservación de históricos superiores mediante suspensión explícita.

## Evidencia reproducible
- Agregado propio:43métodos Python y27scripts Node aprobados; los subcasos/frames tienen sus propios conteos, no se suman como pruebas equivalentes.
- Revisión independiente:423invocaciones/103operaciones/24.324pasos sin alertas;26descargas C/H exactas,13harnesses C17 estrictos,14comparaciones nativo/simulador y4main descargados.
- Auditor UI independiente: navegación normal/paso/reversa, código+imagen+memoria simultáneos, descargas C/main compiladas, JPEG abiertos y guías revisadas. Detalle: evidence/visual/review.md y qa_ui.
- La aplicación reproduce instrucciones mediante intérprete/simulador. Las ejecuciones C nativas citadas se realizaron en QA, no como una nueva compilación nativa dentro de la app.

## Paquete y reversibilidad
El directorio local deliverables contiene aplicación limpia, overlay, rollback, evidencia independiente, manifest.json y SHA256SUMS.json. La primera extracción fresca aprobó toda la suite (43métodos Python y27scripts Node), hashes forward y reversión byte-exacta al original. La comprobación del paquete final queda registrada separadamente en verification.json y sus logs; no debe inferirse sólo de una guarda OpenSpec. Para ejecutar QA del paquete se extraen aplicación y evidencia en el mismo directorio padre, según qa/README.md.

Original5052 y ZIP original preservados; reparación en5053 con cookie/cache propios. No hubo publicación, push, despliegue en VPS ni cambios al PC del usuario. No se ejecuta rollback automáticamente.

## Límites que permanecen visibles
1. **Libro/grafos no están igualados completamente:** persisten11firmas incompatibles y diferencias contractuales preexistentes. Sólo se añadió el guard mínimo autorizado ante fallo de reserva en grafo.c/h; el libro ya ofrece garantías superiores. Word/PDF intactos. Informe y manifiestos de concordancia incluidos en evidencia independiente. Convergencia canónica pendiente de decisión, sin degradar el libro.
2. **Coordinador IA:** entregable separado; ejecutor fixture probado, ejecutor IA real no operativo/verificado. No se promete autonomía.
3. **QA finita:** viewport de escritorio1165×757; no certifica todos los anchos, lector de pantalla, clipboard nativo, todos los atajos, plataformas o entradas. Controles ocultos no fueron forzados. La suite histórica530 no está reproducida.
4. El cierre histórico del guard grafo07:06 es una fotografía de aquel estado; la narración API posterior está autorizada por decisión UI020 y cuenta con revisión final actual. No se reescribe la evidencia anterior.

---
## Historial de notas previas (fotografías fechadas; no estado actual)

# Reparación pedagógica — notas de entrega en preparación

**Estado 2026-10-27 08:39 UTC: trabajo en curso, no declarar toda la aplicación cerrada.**

## Qué se conserva
- Original local y ZIP intactos; servidor5052 no sustituido. Reparación y pruebas en copia5053 con sesión/cookie separadas.
- Código C del libro no se reescribe para acomodar animaciones. Única modificación nativa actual: guarda mínima de extremos de arco ante malloc fallido, change independiente `cloud-graph-invariant-20261027`; firmas preservadas.
- Históricos incompatibles con int C32 se preservan y se avisa; no se borran automáticamente.

## Evidencia y límites
- La afirmación histórica README de530tests/89% no es un resultado reproducido aquí. El ZIP no incluía esa suite; las nuevas pruebas están en `qa/` y evidencia vecina `qa_trazas/`, `qa_ui/`.
- Última corrida agregada Python:26métodos PASS en111.800s (subcasos amplios dentro de cada método); JS `qa/test_*.js` PASS. Son conjuntos finitos, no garantía sobre entradas arbitrarias.
- Matriz independiente backend:423invocaciones/103operaciones, líneasC/encadenamiento/estadofinal/narración verificados.
- C descargado:26C/H,13TAD compilados/ejecutados y sanitizadores; main9exactos+70operaciones,9balances malloc/free. Tras el parche grafo se repitieron4descargas y main,30fallos de reserva con comparación nativo/intérprete y64casos de19operaciones.
- UI sorting:11algoritmos completos y controles/variantes/descargas dentro de matriz definida, cerrado por auditor independiente. Secuenciales cerradas07:33 en29operaciones visibles/6TAD; jerárquicas cerradas08:25 en33operaciones/4TAD y complementarios definidos; grafos en curso, hash pendiente UI.

## Uso en clase
- Comprender ofrece acción/cambio/motivo contextual y conserva referencia avanzada opcional.
- Vista sorting mantiene código, imagen y memoria visibles sin desplazar la página al avanzar; líneas C largas se ajustan sin cambiar el texto descargado.
- Identidades de memoria son simbólicas, no direcciones reales del proceso C. Reservado/liberado/alias deben leerse según el paso actual.
- Descargar main incluye helpers de aplicación explícitamente identificados cuando no pertenecen al API exportado del TAD.

## Cuestiones no resueltas por este paquete
- Igualación canónica libro/web grafos:11firmas y29cuerpos distintos ya existían; libro presenta mejores contratos de estado/reserva. Se espera decisión de migración, no se cambia silenciosamente API/Dijkstra/Kruskal.
- Coordinador OpenSpec separado: puente y ejecutor fixture probados; piloto real IA bloqueado por entorno/conexión. No prometer agentes autónomos operativos. Sus archivos/bundle son independientes de las reparaciones Flask/UI.
- Límite de capacidad pedagógica hash medido, implementación/revisión pendientes al llegar a esa familia.

## Reproducción local
Desde raíz `app`, usar el venv existente (sin instalar dependencias nuevas):
```
python -m unittest discover -s qa -p 'test_*.py' -v
for f in qa/test_*.js; do node "$f" || exit; done
```
Algunas pruebas nativas requieren gcc disponible; no usan red. Las pruebasUI y sus capturas son distintas de estas suites y no se infieren de un resultado backend.

## Corte 09:05 UTC
- Grafos: 16 acciones visibles normal/paso ejecutadas; seis algoritmos hasta el final, retroceso y liberación auxiliar. JPG panel/global completos verificados. Pendientes retests guía15 y narración de retorno NULL, ambos cambios revisados.
- Hash: baseline UI capacidad129+clave3:7 preservado; política128 backend implementada y revisada independientemente (3grupos propios+3independientes). Suspensión antes de reconstruir, historial/main exactos y cero escrituras GET/rechazo en sesiones legacy/versionadas. UI pendiente.
- Agregado Python anterior a estos últimos cambios:36métodos PASS en133.376s;23scripts Node ejecutados sin fallos registrados. Repetición final aún pendiente.
