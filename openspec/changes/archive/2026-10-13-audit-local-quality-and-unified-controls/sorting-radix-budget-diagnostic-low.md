# Radix LOW: diagnóstico del presupuesto de pasos

## Clasificación y origen exacto

`tests/test_sorting_radix_baseline_low.py:78` introduce `assert len(d['steps'])<5000`; línea76 identifica el ID y77 ejecuta **SortingInterpreter**, no la API ni un renderer. Ese `steps` es RadixTape: `app/domain/sorting/radix_tape.py:32` devuelve longitud de registros lógicos. No mide frames JSON, páginas, DOM, bytes o tiempo. Fue una expectativa auxiliar del baseline LOW, compatible con trazas agregadas antiguas. No hay fundamento5000 en C/H, assignment/proposal/specs/plan ni runtime; las otras referencias5000 en docs son campañas de pruebas, no Radix. `git ls-files -- tests/test_sorting_radix_baseline_low.py` vacío: archivo baseline aún no tracked. No inferir autor/aprobación desde eso.

Contrato: `app/adapters/sorting_adapter.py:25-27` UI1..80/int32; C tiene guardas NULL/n0 y malloc, no cap5000. `sorting-radix-instruction-review-plan.md` exige todos los controles, sin cortes porfixtures; la autorizaciónMEDIUM conserva39IDs/C_H. `proposal.md` prohíbe debilitar pruebas. No se localizó un requisito aprobado de5000 ni un SLA de latencia. La evidencia no autoriza cambiar silenciosamente el test.

Los límites de transporte reales son `app/services/radix_trace_service.py:154-155`: denso<=2048eventos **y estimación**<=32MiB; no límite JSON duro de32MiB. Página<=128 en142-143; cliente4pages64+seed16; store128MiB/32trazas/TTL900s y2builders. Referencias exactas: source-references.json. Estos presupuestos fueron registrados en sorting-radix-metrics-and-representation-decision.md, no justifican el5000.

## Cota para todo el dominio admitido

m/p=negativos/no-negativos,n=m+p; aNeg/aPos=asignaciones a maximo, cada una<=tamañoGrupo-1; dNeg/dPos=dígitos procesados,<=10; positivos todoscero tienen dPos=0. Conteo de las fronteras del observer vigente:

`E = 27 + 12m + 10p + I(p>0) + aNeg + aPos + dNeg(12m+45) + dPos(12p+45)`.

El helper aporta12*tamañoGrupo+41eventos por llamada, más4eventos del caller por dígito. Con ambosgrupos,no más de924+133n; sólo negativos476+133n; sólo positivos477+131n. Por n<=80, E<=11564. Se alcanza con79negativos de magnitudes1000000000..1000000078 y1positivo2147483647: probe C17 nuevo11564/modelo exacto,22alloc22free0live. Sólo ese caso C nuevo se ejecutó; no diez cierres ni suiteglobal. El input original balanceado requiere11408, verificado anteriormente; exigir5000contradice fidelidad completa. La fórmula vale para las fronteras/granularidad vigentes; no es un nuevo cap semántico para futuras instrucciones añadidas.

Cada evento tiene un registro delta o checkpoint:11564registros no son11564frames completos. Checkpointcada128 conserva estado; lectura reconstruye como máximo127deltas. La página materializa<=128frames; el seed16y caché4pages64 limitan la materialización cliente para trazas paginadas. Los densos sí materializan sus frames completos y pueden ser pesados.

## Medidas y evaluación de rendimiento

Diez distribuciones cubren tamaños1/11/23/80, ceros, signos extremos, grupos1/79y40/40,10dígitos, frontera9/10 y frontera densa. Todas ordenaron, conservaron la fórmula y terminaron0live. Son medidas finitas, no benchmarking de todas las2^32posibilidades ni pruebaRSS/concurrencia.

Máximo medido49,272,469bytes retenidos, dentro del store128MiB; paginados envían16frames/~194KB inicialmente. Construcción inicial hasta9.09s (kernel+índice+materialización, no HTTP/red); páginas128 hasta0.30s decode+JSON y hasta3.86MB en muestras. Densos llegaron23,214,063bytes iniciales/7.73s, aunque su tape sólo8.18MB. `resource-measurements.json` separa todos esos campos. Esto demuestra acotación del flujo vigente y viabilidad local de los casos, pero9s/23MBson costos perceptibles: no certificar una experiencia instantánea ni latencia universal sin SLA/medida de carga. El estimador32MiBno mide payload JSON real. Mejorar dense-vs-paged sería una etapa aparte, no razón para borrar instrucciones.

Los DOM2031y replay0POST previos se reutilizan como evidencia MEDIUM, no se repiten ni amplían desde estas medidas backend. Preview5051 no se reinició ni se cambió producto en LOW.

## Resolución propuesta, no aplicada

Clasificar5000como expectativa incorrecta de prueba, no requisito aprobado que obligue rediseñar C. Conservar ID y aserción de resultado; reemplazar únicamente la expectativa arbitraria por **igualdad de todos los eventos con C nativo** del mismo input11408, métricas.steps congruentes y retorno/cleanup0live. Así se fortalece fidelidad en vez de ampliar un límite para lograr verde. Mantener aparte gates de páginas/ownership/TTL/cache/retención; el test ya tiene esos nueve gates MEDIUM registrados. Cota11564y caso alcanzable fundamentan revisión del dominio, no fixtures productivos.

Original SHA60360fc8de84c4ef3027be636732c59005eb54bcd5a818de4ead0124c0ef197d y copia original-test-preserved.py preservados. Este LOW **no modifica** prueba ni su expectativa. Recomendación concreta para coordinación: aprobar corrección explicada del mismoID, guardar original/SHAy supersesión, ejecutar gate afectado y diagnóstico nativo antes de consolidar. Alternativa: conservar rojo yRadixabierto. No ocultar fallo, noxfail, no renombrar steps ni comprimir su conteo lógico para eludirlo. Test anterior38/39y47/48 se informa sin rerun;10/11/global13/22/docs121/208igual.
