# Cierre finito
UI16acciones y12pantallas smoke aprobadas10:58UTC. Primera extracción55Python/
8Node canónicos y34Python/25Node no-grafo PASS11:03:37UTC; rollback exacto.
Ver LEAD_FINAL_REVIEW.md y verification.json del paquete final. Lo que sigue
conserva cortes históricos, no el estado actual de pendientes.

# Integración canónica — estado 2026-10-27 10:26 UTC

La segunda copia adopta el C/H extraído del libro, sin modificar sus bytes. El
intérprete ejecuta ese subconjunto de C; la aplicación no compila C nativo en cada
solicitud. La compilación/ejecución nativa corresponde al oráculo independiente.

## Verificado hasta este corte
- Motor: comparación independiente de 313 escenarios nativos y 14 trazas con
  4.882 transiciones continuas. Véase `../qa_independent/ENGINE_CANON_REVIEW.md`.
- Integración propia: 6 pruebas de servicio, 2 HTTP/sesión y 2 de presupuesto.
  Historial antiguo/no válido se conserva suspendido, no se reinterpreta ni trunca.
- Los fallos C reales conservan su traza y su efecto, incluidos fallos de la segunda
  llamada de una inserción no dirigida. No se inventa una transacción conjunta.
- 34 pruebas Python de regresión de los otros doce TAD, y 25 archivos Node, pasan.
  Reproducir con `run_non_graph_regressions.py` y `run_non_graph_node.sh` desde app.
  Los fixtures vecinos proceden del paquete de evidencia congelado de reparación.
- El test antiguo de extracción textual del handler `graph create` no corresponde
  al nuevo handler común: su fallo se conserva en `non_graph_node.log`. No es una
  regresión de otra familia ni se borró el test. Los tests nuevos del handler
  canónico lo sustituyen para esta versión. Los tests Python `test_graph_*` de la
  primera reparación son contratos anteriores, no un certificado de esta versión.

## Límites explícitos
- Captura completa hasta 4.000 eventos C/caller y una publicación final. Preflight
  en copia sin snapshots; por encima, paso rechaza sin escribir sesión. Normal
  ejecuta completo sin guardar una traza extensa. No se muestrean instrucciones.
- Inyección QA `fail_allocation`: se conserva el historial y el efecto real, pero
  no se ofrece un main con malloc ordinario como si reprodujera la inyección.
  La reproducción nativa de estos fallos usa el harness de QA independiente.
- La instancia 5054 y las pruebas no-write usan `SESSION_REFRESH_EACH_REQUEST=False`;
  la configuración general heredada puede renovar TTL/cookies al leer sin alterar
  el contenido del historial.
- La revisión independiente integrada HTTP/servicio/presupuesto está aprobada:
  19 operaciones pareadas,3.788pasos,7gruposHTTP; 359casosno-grafo sin discrepancias.
  La UI real5054 aún está en curso. No está
  cerrado el cambio ni preparado un paquete final de convergencia.
- Checkpoint de reparación 5053 y su ZIP permanecen intactos y separados. Los
  documentos Word/PDF originales siguen sin modificación. IA autónoma no activada.

## Fuente del libro verificada independientemente
`../qa_independent/book_alignment/INFORME_FINAL_FUENTES.txt`:26descargas exactas;
grafoC/H iguales a la reextracciónWord; otros24C/H iguales al checkpoint.168cuerpos
impresos coinciden (44grafo+124otros),48funciones extraweb no están impresas. No es
una afirmación de identidad byte a byte del libro completo.

## Suite propia consolidada — 10:28 UTC
54métodos Python canónicos PASS en82,135s (`canonical_python_all.log`),
5archivos Node canónicos PASS (`canonical_node_all.log`). Son pruebas nuevas y
finitas; las revisiones independientes y los casos UI se cuentan por separado.
