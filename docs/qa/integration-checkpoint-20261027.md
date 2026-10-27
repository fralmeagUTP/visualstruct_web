# Candidato de conciliación del 27 de octubre

Este checkpoint conserva la versión entregada y concilia pruebas históricas con `graph-book/v1`, vista de clase, consola, ayuda y controles actuales. No afirma que todo CI esté aprobado ni autoriza desplegar un SHA fallido.

## Evidencia finita comprobada

El commit previo `4475dfc71c77fc2aa90ee80ac7d90718446f24ab` pasó C17 y AddressSanitizer/UBSan remotos: [ejecución](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/40520382180). Los 26 archivos C/H permanecen idénticos a la entrega. `.gitattributes` evita que Git altere sus finales de línea en Windows y preserva snapshots y recibos vinculados por bytes.

Las comprobaciones locales están documentadas por sus propietarios, sin sumar grupos solapados:

- 75 pruebas de paridad nativa de caminos/MST y 26 de rutas/trazas.
- 31 E2E: 29 casos del archivo principal y dos consultas de vecinos.
- 338 pruebas relacionadas con fixtures, más controles de integridad/publicación; 2.325 entradas auténticas verificadas.
- Recorridos, memoria, errores, transporte y contratos de grafos: documentos específicos de migración.
- Los 110 casos originales de los once algoritmos de ordenamiento y recorridos/descargas nativos asociados.
- Controles de falsificación de fuente, estados, ledger, referencias, recibos y privacidad de diagnósticos.

Los workflows conservan sus gates. Los diagnósticos seguros ahora registran también errores de colección, sin publicar tracebacks o entradas privadas. Las pruebas de esos hooks usan un módulo aislado para no perder sus propios informes en el ledger real de CI.

## Trazabilidad y pendientes

Los archivos históricos se recuperan por bytes originales, con SHA y tamaño; la extracción selectiva evita repetir unos 475 MiB por auxiliar. Ningún resultado histórico se presenta como una ejecución nueva.

El runtime de la entrega tiene SHA `9c053251f39f44681479d312f42a1f882bbb8fcf4bf048bae8cc83843b145456` y coincide con el ZIP del usuario, SHA `004d35d9a06dcce619a6ff05f24eac6165ec5dd97e79a9e6b79f60567573307b`. Su recibo conserva el preimage auténtico del runtime aprobado anterior. Este vínculo nuevo no exime las referencias históricas.

Sigue pendiente el informe `dfs-transport-jpg-canonical-integration-independent-review/review.md`: esperado `575ce6e9c64cadb19e1e141b1ca8a52f1eea6421e0de9bd1cf1a91a25ff64077`, disponible normalizado `3c1d3bdda458d61d1a96df4d406cb894f4834d6fce9b4f2ce8602ec7896e448f`. No se cambió ese esperado ni se aceptó el archivo como si coincidiera. La discrepancia permanece visible y hace fallar el control de esa referencia. Tres revisiones Git, los ZIP pertinentes y 2.439 blobs Git de tamaño pertinente no recuperaron la preimagen requerida.

La migración de algunos E2E históricos de recorridos y el barrido restante de pruebas continúan por separado. Un auxiliar nuevo contó tarjetas `V1,V1` de dos paneles como si fueran una única lista: se corrige para comprobar cada panel y la memoria completa. Esa aserción no constituye por sí sola un defecto de la aplicación. Los resultados completos del próximo CI deben revisarse antes de declarar el candidato listo.

No se fusiona `main`, no se modifica el Docker local verificado y no se despliega al VPS desde este trabajo de conciliación.
