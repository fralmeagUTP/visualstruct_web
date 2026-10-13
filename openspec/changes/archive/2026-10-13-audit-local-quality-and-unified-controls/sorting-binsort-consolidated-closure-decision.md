# Binsort: consolidación LOW y cierre con alcance explícito

Fecha UTC: 2026-10-02T21:32:01.509197+00:00. Proyecto canónico D:\MisProyectos\Web_VisualEstruct. Asignación coordination-sorting-binsort-consolidated-review-low-20261002; operación sorting.binsort-expanded-fidelity. La instrucción nueva sorting-binsort-consolidated-review-authorized-low.md autoriza cierre justificado y luego baseline LOW de Radix.

## Decisión

Binsort se registra como décimo método de once bajo el dominio UI vigente observado: 1..80 enteros int32, éxito con k=max-min+1<=1.000.000 y modelo C-equivalente de rango rechazado y reserva NULL controlada, en entorno Windows/int32/size_t64. No hay brecha funcional abierta detectada en ese alcance. Los nueve métodos previos conservan sus cierres y fuentes; global13/22 y ledger121/208 no cambian.

El cierre no procede sólo de ocho muestras verdes. Se apoya en el núcleo Counting ampliado previamente verificado y byteidéntico, revisión estructural del decorador Bin/codec y contratos, oráculos causales completos, pruebas permanentes y UI. No se afirma demostración formal ni comprobación exhaustiva de todas las entradas/caminos. El checkpoint MEDIUM anterior exigía esta revisión y queda conservado como historia.

## Requisito, regla revisada y evidencia

| Criterio | Regla vigente | Evidencia |
|---|---|---|
| Dominio completo admitido | Adapter rechaza vacío, n>80, bool/float y fuera-int32. Todo Bin usa una vez Count sparse; no n4/k4 ni otra ruta agregada | source-review.json; 60 IDs vigentes; normal, negativos, n80, nearINT_MIN/MAX y k1m |
| Delegación y scopes | Initial aparece una vez; entrada y call Bin preceden Count, retorno propio lo sucede. Cada registro no inicial se conserva en índice+2 y cada zero_span mantiene límites. Parámetros arreglo/n y alias se suspenden, retirándose Bin sólo en su retorno | 4.341 eventos de ocho éxitos congelados; 462 de cuatro errores observados en contexto Bin; preservación de todos los registros físicos máximos y fronteras de spans |
| Compresión exacta | Cubeta cero emite test del for=true, test del while=false e incremento; mismo array/counters/scopes y i/previous/changed por fórmula. No se materializan millones de conteos | CountingTape y BinTape byte/revisión; oráculos completos y spans máximos. Dos streams Count reutilizados, sin repetir suites del método cerrado |
| Recursos y transporte | <=n cubetas ocupadas y <=n+1 huecos => O(n) registros físicos independientes de k. Estados O(n), bytes retenidos O(n²) con n<=80. Dense/paged sólo presupuesto de transporte; pages<=128, ventana64, caché4pages64+seed16; store32/128MiBcontabilizados/FIFO/TTL900s y2builders | UI80/k1m:3.000.912 eventos,1.231registros,12.744.946bytes retenidos,134.997bytesinitial. No claim de RSS ni recuperación OOM/concurrencia global |
| Errores y aceptación | Guarda de rango antes de reservar; parámetros Bin viven tras error_return del callee y se retiran en Binreturn0. Estado aceptado completo/main/historial intactos. ModelMemoryError y rechazo de transporte son distintos | cuatro errores C/API, QA privada sólo TESTING, modelo plain y memoria de entrada del hook legacy; 3 probes sensibles actuales,3pass1.30s |
| Replay y ownership | /step explícito/implícito usa source guardado; sin traza404, owner ajeno/reset404, expiry410; GET noSort/noTTLrenew. UI/export separan intento de estado aceptado | 60 IDs y probes UI del MEDIUM reutilizados; preview actual assets/C_H por bytes, normal73eventos/step delegado, fast-step/cinco secciones sin JSerrors |
| Caller y documentación | Un run aceptado conserva efecto y llamada C; fallo no entra en main. Cuatro callers antiguos por bytes exactos y uno nuevo80/k1m | C17/Doxygen0avisos; nuevo1malloc-equivalente calloc/1free/0vivos, fault seguro de primera reserva aparte. Caller no sustituye oráculo por instrucción |

## Vigencia y no repetición

60IDs únicos=32 originales intactos+28 nuevos. Su unión está documentada en summary del MEDIUM; no sumar logs solapados, restauraciones, programas ni pruebas repetidas como nuevas. source-review verifica todos los hashes de las nueve fuentes protegidas, C/H y runtimes; el diff compartido actual coincide con la fotografía final MEDIUM. Se fija también SHA actual de módulos Bin y shared integration.

Este LOW no cambia código productivo ni reejecuta suites cerradas. Ejecuta sólo tres IDs existentes Bin antes de cerrar: rango ERROR, MemoryError del modelo y preservación del decorador máximo n2/k1m. 3pass1.30s son subconjunto de60. Vista local127.0.0.1:5051 canónica comprobada, sin reinicio.

## Plataformas, simulaciones y límites

Observado: Windows10 build19045, Python3.10.5, gcc targetx86_64-w64-mingw32/C17 e int32/size_t64, Chromium147.0.7727.15; toolchain.json registra versiones exactas. No se certificaron ABI32bit, Linux/macOS ni otros navegadores. SIZE_MAX=true no se alcanza con k<=1m bajo size_t64; no se ejecutó full-span32bit inseguro.

NULL se inyectó con un allocator controlado en C y appTESTING; no es agotamiento real. La UI NULL usa una respuesta TESTING interceptada y rotulada, no allocator de producción ni recarga de esa simulación. Los errores de rango UI sí son HTTP reales en preview. Todas las trazas del modelo declaran real_c_execution=false. MemoryError de Python no representa por sí solo fallo observado del malloc/calloc C; el hook legacy conserva aceptación sin fabricar una traza nativa. Rechazo de store no inventa ERROR C.

Los digests máximos reutilizados cubren campos escalares y fingerprints ponderados colisionables; no snapshots completos de cada celda de un millón ni prueba universal. UI grande muestrea fronteras, no recorre sus tres millones de frames. Memoria contabilizada no es RSS; store efímero pierde referencias tras reinicio sin auto-sort. NULL/n0/helperNULL nativos externos no amplían el dominio UI que los rechaza antes de ejecutar.

## Continuación

Cierre Bin comunicado antes de ejecutar Radix. La misma instrucción autoriza preparar/iniciar el baseline LOW Radix, con nueva asignación, bindings y guarda before. No tocar semántica C/H ni adaptar los diez métodos cerrados a fixtures. Auditoría global, otros módulos y QA final permanecen abiertos. No commit/push/merge/despliegue.
