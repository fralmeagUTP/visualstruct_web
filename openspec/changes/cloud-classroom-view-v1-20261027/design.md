# Diseño aprobado de alcance
Módulo de presentación compartido (JS/CSS) y hooks mínimos en las cinco familias.
No cambiar fuentes C, productores de trazas, resultados, HTTP ni historial.
Viewport de imagen dominante de altura disponible, sidebar C estable con scroll
local. Tamaño inicial100% legible; controles de zoom explícitos y pan local
conservados al repintar, retroceder y abrir memoria. Nunca usar auto-fit por paso.
Memoria completa disponible mediante control cerrado inicialmente; en secuenciales
los nodos/enlaces del propio TAD son la imagen principal, no se ocultan como
«memoria». Separar sólo detalles auxiliares/diagnóstico.
Resultados: paneles/tabs de consola,main y estructura, alto acotado, copia de texto
C real y ampliación reversible sin recargar ni ejecutar operaciones. Mantener IDs
y referencias para que las actualizaciones sigan llegando al mismo panel.
Preservar exportaciones completas de clones sin modificar la vista viva.

## Compatibilidad de pruebas DOM
Los renderers añaden metadatos de copia al `dataset` estándar de elementos HTML reales. Tres fixtures históricos (`qa/test_real_stdout.js`, `qa/test_stdout_raw_renderer.js`, `qa_convergence/test_book_frontend_stdout.js`) carecían de esa propiedad. Se permite completar exclusivamente esos mocks, conservando copia anterior y diff literal sin cambiar assertions. No se modifica el comportamiento de producción para satisfacer un DOM incompleto. Los logs fallidos se conservan y el retest debe quedar explícito.

## Protección de la pantalla activa (11:54 UTC)
El parent confirma que no se debe redimensionar la pantalla compartida del usuario. El segundo viewport es opcional si puede verificarse de forma independiente sin impacto; su ausencia se declarará y no sustituye las comprobaciones obligatorias de cinco familias en 1165×757.
