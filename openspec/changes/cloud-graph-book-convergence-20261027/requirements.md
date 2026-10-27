# Criterios de aceptación
- GB01: tad_grafo.c/h descargados idénticos byte a byte a la extracción canónica y hash registrado;30públicas+14auxiliares disponibles, sin cola externa.
- GB02: cada uno de los8GrafoEstado se representa explícitamente; no confundir NULL con error ni valor0 con ausencia.
- GB03: inserción falla atómicamente ante cada malloc alcanzable; eliminación retira incidentes dentro de C, sin caller duplicado.
- GB04: BFS/DFS conservan marcas al fallar y publican sólo al éxito; cola de índices/recursión según fuente real.
- GB05: límites int32 y acumulación longlong, NO_EXISTE, negativos, ciclos alcanzables/no alcanzables y rangos concuerdan con oráculo nativo.
- GB06: Prim/Kruskal conectado/desconectado/asimétrico y singleton respetan estado/propiedad/liberación del libro, no contrato web anterior.
- GB07: memoria propia/prestada, reserva/liberación e inicialización fieles; sin lecturas muertas/indeterminadas ni direcciones reales inventadas.
- GB08: código/variables/estado/explicación sincronizados por instrucción, cursor reversible y resultado normal equivalente; no planes antiguos bajo código nuevo.
- GB09: main del historial/guías/snippets compilan con C/H nuevos y muestran cambios de contrato; no resultados precalculados.
- GB10: versión de contrato/sesión evita checkpoints e historias reinterpretados silenciosamente; conservar exportación o requerir reinicio explícito cuando no sea seguro reproducir.
- GB11:12familias no grafo conservadas; regresiones existentes y UI común no degradadas. Pruebas antiguas de grafo se clasifican como contrato sustituido o regresión real, sin borrarlas para dar verde.
- GB12: revisión independiente y UI5054 con datos aislados; paquete separado y comprobación byte-exacta de checkpoint5053 intacto.

## Precisiones de aceptación aprobadas
- GB03 es por llamada C canónica. En modo no dirigido, el llamador realiza dos
  inserciones independientes: sólo inicia la inversa si la primera termina OK.
  Si la segunda falla, se conserva y explica la primera; no se inventa rollback.
- GB05: la protección contra desbordamiento se comprueba en sumar_seguro con
  oráculo nativo (retornos0/1); el mapeo del caller a GRAFO_RANGO se inspecciona
  en la fuente. No se afirma una emisión pública de estado7 end-to-end bajo15v/int32.
- GB08: hasta4.000 eventos C/caller más una publicación API se conserva la traza completa; por encima se rechaza
  preparar pasos sin mutar sesión, o normal ejecuta sin traza con aviso explícito.
  La autorización y mediciones están en design.md. No se recortan pasos.
- GB09: un historial con inyección QA de malloc no se ofrece como main docente
  ordinario que fingiría reproducir ese fallo. Se conserva/exporta y se remite al
  harness diagnóstico. Los historiales normales sí generan main compilable real.
