# Hash stats MEDIUM checkpoint: LOW pendiente

Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Asignación coordination-hash-stats-instructions-medium-20261003; operación hash.stats-instructions-medium. Nueva instrucción confirma opciónA: conservar API y distinguir cálculo C. Sin nuevos contratos ni cambios de C/H/H1. Guarda before0; after se guarda con fuentes frescas al terminar.

## Resultado y alcance

Corregidas las tres regresiones de bodies/scopes/caller. Fuente real incluye caller THEstadisticas, char texto[512], th_estadisticas y th_formatear_estadisticas originales. Motor dedicado por instrucción: {0} inicializa cinco campos semánticos int/int/int/int/float; guardas, i/actual/nodos_en_bucket/bucles, ocupados y colisiones, conversiones y división float, retorno/copias, buffer/terminadores/truncamiento y scopes propios. El caller recibe copia; el formateador llama de nuevo y recibe otra copia, excepto guardas que retornan antes. Las dos instancias internas tienen identidad distinta. No se inspeccionan padding/ABI ni se leen campos/bytes indeterminados.

API conserva tres campos con cociente Python; metadata seis decimales/mensaje tres. C convierte ambos operandos a float y asigna float; texto dos decimales. Ejemplo2/3 API0.6666666666666666 frente C0.6666666865348816, mostrado explícitamente sin ocultarlo ni forzar igualdad. C y API no cambian su semántica. El caller real imprime stats-C, stats-API-projection y stats-format calculados por C, con double para la proyección equivalente a API en host verificado. Journal conserva dos consultas genuinas, incluso iguales, tras recarga; no cambia historial mutante. Kernel no imprime ni reserva/libera.

## Evidencia finita y conteos

145 IDs únicos =134previos+8baseline+3nuevos: todos pasan en88,97s. Ocho tests baseline sin modificar;134tests previos protegidos. Foco final11pass9,86s tras fortalecer conteos exactos del observer, solapado con145 y no agregado. No se repitieron once Sorting ni otros bloques cerrados para inventar cobertura; hashes protegidos conservados.

Cuatro fixtures originales (vacío3,colisiones3,disperso7,destruido) y27muestras de buffer/guardas0,1,2,8,64,512 másNULLtabla/tabla0/destinoNULL. Misma referenciaC_H ycanarios/harness físico1024 conA5; motor distingue almacenamiento de capacidad pasada. Observer de C original sólo con callbacks QA:1658eventos/542condiciones/1424snapshots de campos coinciden con la traza y buffers; firmas/tipos/root/destino aliases afirmados enC17. Las máscaras describen inicialización semántica C, no memoria física de padding.

Cuatro probes aritméticos aislados verifican convertir numerator/denominator antes de dividir (2/3,4/7,16777217/16777219,INT_MAX/(INT_MAX-1)); cero tablas gigantes/allocaciones de esos probes y no son cuatro fixtures extra de método. Hostbinary32/double53 verificado nativamente; no ABI/plataforma/modo de redondeo alternativo certificado.

Ocho observaciones API mantienen las diferencias originales en cuatro casos repetidos; API integer fields y metadataocupados/colisiones iguales alC. UI real ocho consultas:634frames/626back,cinco secciones,0JSerror/POSTextra,recarga conserva trace y dos llamadas porcaller. UI yAPI porfixture descargan mains con mismosbytes: cuatro programas únicos,no ocho. C17 estricto/Doxygen0; ochoresultadosC,ochoAPIproyecciones yochoformatos contrastados con referencias. 16alloc/16free/0vivos y16NULL simulados, sin OOMreal. Cleanup no cierra clear/destroy.

Recursos de las mismas ocho observaciones: picoPython27.772.305bytes,JSON2.524.174bytes,máximo2,9227579s instrumentados, incluyendoFlask/session/serialización. No RSS/SLA ni capacidad arbitraria.74archivos protegidos idénticos; siete puntos de integración/documentación previstos cambiados más motor/tests/docs propios.

Fallos intermedios sóloQA conservados en qa-corrections.md: callback sinllaves, escaping de probe y selección incorrecta de fixture tabla0. No motivaron cambio producto. Logs compilación originales preservados; rawstderr yJSONL separados. native-observer-final.log contiene contraste final.

## Límites y siguiente paso

snprintf opaco, formatos decimales exitosos, hostfloat/double verificado finitamente, identidades simbólicas por operación. Sin errores libc/sanitizadores/ABIalternativo/capacidadesarbitrarias/sesioneslargas/tiemposuniversales. Los probes numéricos no cierran stats fuera de cuatro fixtures. PreservadosH1/C_H/8Hashcierres/11Sorting; sinADDED/publicación/commit/push/merge/despliegue. El rechazo anterior ADDED sigue documentado y ese spec no existe.

Hash sigue8/11 hasta consolidación LOW stats; clear/destroy_table después conasignaciones propias. Global13/22,docs121/208,C1 1/12 unchanged. Preview propio en5051 verificado identidad/HTTP200 y preservada caché; guía no normativa docs/qa/hash-stats-guide.md. Handoff C1 propio c1-evidence-handoff.json; matriz/progreso ajenos no modificados. Siguiente revisión LOW del scope/tipos/copias/float/buffers/evidencia/recursos antes de cerrar sólo casos registrados de stats.
