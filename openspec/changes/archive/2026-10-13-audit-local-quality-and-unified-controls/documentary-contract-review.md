# Contratos documentales y decisiones pendientes

## C-GRAPH-BFS-NEGATIVE-01 — corregido por aprobación explícita
La discrepancia histórica -1 se corrigió con autorización del usuario: se retiró la comprobación centinela únicamente dentro de la guarda de cola no vacía. Se preservó cola_desencolar vacía y los demás contratos. Evidencia/compilación/pruebas en evidence/bfs-approved-fix. La revisión por instrucción de todos los algoritmos de Grafos continúa abierta. La nota anterior NO aplicado era histórica; se conserva en la evidencia antes de esta actualización, no describe el estado actual.

## HASH-DOC-CONFLICT — consolidación pendiente
La spec vigente conserva referencias a claves de texto/rehash que contradicen el cambio archivado de capacidad fija y claves enteras, y el C actual. Mantener comportamiento actual. Propuesta: consolidar documentación canónica hacia el contrato entero/capacidad fija, preservando historial y sin implementar rehash. Requiere resolver la intención documental antes de cerrar decisiones; detalles por compromiso en reconciliation-detailed.md.

## Revisión Doxygen por símbolo
El catálogo actual regenerado registra 479 miembros y 382 entradas de función; agrupando por archivo base/símbolo hay 208 entidades de función. Ver documentation-symbol-signoff-ledger.md y JSON SHA para estados exactos. Doxygen puede combinar documentación entre .h y .c: cero advertencias colectivas NO prueba documentación autónoma de cada archivo ni exactitud semántica. Revisión por archivo y contratos restantes sigue abierta.

Correcciones aplicadas: ayuda de búsqueda en lista describe todas las coincidencias, no terminación en la primera; comentario C/H de búsqueda ajustado; cp_vacia incluye cantidad cero; postcondiciones de encolar/desencolar se limitan a éxito; cp_frente documenta false para parámetros inválidos/vacío. Tokens C verificados idénticos antes/después por apply_audit_stage.py. No se marca completada la tarea documental global.

## Verificación documental autónoma completada
26 archivos HTTP actuales: Doxygen 1.18.0 con EXTRACT_ALL=NO, EXTRACT_STATIC=YES, WARN_IF_UNDOCUMENTED=YES, WARN_IF_DOC_ERROR=YES y WARN_NO_PARAMDOC=YES: cero advertencias en cada archivo aislado y también en el conjunto. Informe antes/después y hashes de bytes adjuntos. Se documentaron 40 declaraciones/definiciones, etiquetas de parámetros/retornos, typedefs y campos faltantes. Los contratos públicos idénticos C/H evitan duplicaciones; notas de implementación originales se conservan como comentarios ordinarios. Tokens C sin cambios, comprobados antes de cada escritura.

Correcciones contractuales adicionales: ABB mínimo/máximo admiten NULL; insertar documenta fallo de malloc conservando raíz existente; AVL mínimo requiere nodo no NULL; costo de arco -1 puede indicar ausencia o peso válido; BFS documenta propiedad del resultado, marcas y memoria parcial, y la discrepancia negativa vigente, sin cambiar conducta.

Esto cierra la comprobación de documentación por archivo y generación, no la exactitud semántica completa de todos los símbolos ni el manual global. Casilla global continúa abierta.

## Pendientes exactos y cierre Lista
Ocho contratos de Lista (siete visibles + CrearNodoLista) revisados con código y observaciones nativas, incluyendo NULL/malloc/posiciones/propiedad. Quedan 200 entidades sin cierre completo: 13 con evidencia parcial, 187 sin cierre individual registrado. La tabla documentation-symbol-signoff-ledger.md identifica cada símbolo por archivo. Manual/ayudas: 13 rutas HTTP200 no equivalen a 13 contratos completos; se corrigió adicionalmente la falsa afirmación de inserción ordenada de Prioridad. Casillas globales permanecen abiertas.


## Miembros nofunción y criterio13 aceptado 2026-10-04

[Checkpoint vigente](documentary-nonfunction-global-criteria-checkpoint-low.md) y [decisión criterio13](documentary-c-h-criterion13-acceptance-decision-low.md).34declaraciones iniciales/tipos/campos/enums y fuente completa revisados; sólo8C/Hcomentarios, tokens/preprocesado/5objetosidénticos, HTTP/compilación/Doxygen reales y bindings actuales. Se marca exclusivamente fila13 de descargasC/H/compilación/Doxygen/exactitud;14/22derivado, ocho criterios abiertos con pendientes/condiciones precisos. No suites/algoritmosnuevos, no repetir26/67/Heap20/Desapilar. Bloqueos antiguos H1/Graph/RN/Sorting y faltantesdocumentales quedan sustituidos por fuentes vigentes, no por esta fotografía histórica. Preview/Git/owners intactos.
