# VisualStruct — cierre técnico con reservas

Estado verificado: **13 de octubre de 2026**. Alcance auditado: **`c395f5f70072d211fb0654af9b321294305e64b4`**.

La revisión independiente final aprobó este alcance con reservas y sin más ejecuciones necesarias para ese alcance. Este documento guarda el cierre autorizado por el usuario; no certifica estados no demostrados ni actualiza el VPS.

## Resultados finales sobre el SHA auditado

- **1559 pruebas unitarias PASS, sin XFAIL**, e inventario PASS. El job unitario del [run38420905013](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/38420905013) pasó; el run completo permanece **cancelado** por la campaña original de cobertura. Ese historial no se reescribe.
- **34 E2E PASS**, [run38420888254](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/38420888254).
- **13 harnesses C17/ASan/UBSan PASS**, [run38420918688](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/38420918688). `detect_leaks=0`: sin certificación LSan de fugas ni garantía universal.
- **Cobertura y todos los gates PASS**, [run38434724071](https://github.com/fralmeagUTP/visualstruct_web/actions/runs/38434724071). La rama temporal `2e90b076` hizo checkout de `c395f5f`; los resultados se atribuyen al código auditado.

| Cobertura | Resultado |
|---|---:|
| Global | 20.866/24.433 = **85,40%** |
| Sorting | 95,92% |
| Grafos | 96,54% |
| Hash | 99,22% |
| Heap | 93,38% |

La campaña de cobertura registró **1556 PASS**, en bloques disjuntos de618 y938. No se suman al conteo unitario como casos nuevos adicionales. Se verificaron39artefactos y sus hashes,188rutas canónicas, fuentes idénticas y unión exacta de datos crudos, sin promediar porcentajes. Consumió **26,13 de55runner-minutos** autorizados.

El éxito de la campaña sucesora sustituye el pendiente de cobertura del run cancelado, sin borrar su resultado. [Resultados CI guardados](../audit-local-quality-and-unified-controls/evidence/visible-final-c395f5f-three-full-CI-once-low-20261013/final-result.json), [cobertura sucesora guardada](../audit-local-quality-and-unified-controls/evidence/visible-coverage-only55-prepare-QA-low-20261013/final-result.json).

## Alcance educativo y reservas conservadas

Se conservan los66IDs originales aceptados finitamente y los dictámenes históricos R3/R4. MAX15 está implementado; las pruebas funcionales y visuales con8nodos no demuestran todas las entradas hasta15. Correctitud, fidelidad, eventos y pasos educativos siguen siendo centrales.

Sorting no tiene SLA fijo de15segundos. Se distinguen C nativo/intérprete, preparación y transporte, y renderizado/replay humano. La decisión de cesar nuevas optimizaciones no demuestra imposibilidad técnica de mejorar.

Las reservas siguientes son límites históricos o evidencia no demostrada, **no errores actuales automáticamente confirmados**:

- **230 casos históricos** bloqueados por recursos. Un éxito CI diferente no los convierte en PASS bajo sus antiguos límites locales.
- Graph15segundos de ejecución pura y ejecución completa en el máximo de15nodos, fuera del alcance probado.
- **12 XML Counting faltantes**, Counting retention-copyERROR y originales temporales perdidos; no se reconstruyen ficticiamente.
- ASan con `detect_leaks=0`, sin LSan; límites finitos de ABI, UB/OOM, memoria, entradas, caminos, UI y accesibilidad.
- **JPEG Sorting tiene PASS focal local**, con tres exportaciones y comparación de píxeles, en el worktree `e5032dc` más parches. Mantiene su atribución propia, separada de Graph JPEG; los antiguos SKIP no se convierten en ejecuciones nuevas. [Evidencia focal](../audit-local-quality-and-unified-controls/evidence/visible-three-approved-focal-blocks-once-low-20261013/final-result.json).

Los fallos y cancelaciones anteriores permanecen fechados. Los XFAIL anteriores de ayudas no son pendientes actuales del cierre unitario sin XFAIL. Las cifras41,23%,82,01%,83,09% y demás cortes del historial no son la cobertura vigente del cierre.

## Conclusión de entrega

**El alcance técnico auditado de `c395f5f` queda cerrado y aprobado con las reservas expresas anteriores.** No requiere más ejecuciones para ese alcance. No constituye una certificación universal ni acepta por inferencia los estados no demostrados.

El cierre queda guardado documentalmente en este archivo. **VPS no actualizado.** No se ejecutaron pruebas ni se realizaron publicaciones, commit, push, despliegues, reinicios o cambios de producto para esta actualización. Tampoco se archivan cambios ni se admiten requisitos históricos C1 por este guardado.

Para explorar localmente, utiliza el preview existente [http://127.0.0.1:5051](http://127.0.0.1:5051) y el [manual](http://127.0.0.1:5051/help/manual). Su disponibilidad y versión en memoria no se reconfirmaron aquí. Usa entradas pequeñas y un perfil privado si deseas separar tu historial; no hacen falta nuevos ensayos largos para leer la entrega.

## Integridad documental y continuidad

Se modificó únicamente este archivo, bajo autorización directa del usuario. Se comprobaron fuentes, enlaces, diff y lectura posterior. La guarda de continuidad intentada devolvió exit2 por una referencia ausente: `openspec/continuity/assignments/coordination-c1-remaining-documentary-20261002.json`. No se afirma guarda verde ni cierre del protocolo C1. El índice y los registros de asignación permanecen sin modificar.

SHA256 de la versión anterior: `4b8edacfc55c9fc91b9d10e61c10e9a7b65c71814fdf97d0a2bfd6c558f1ff2d`. Esa versión se conserva íntegramente dentro de este mismo archivo, como historia fechada y sustituida donde corresponde por el cierre anterior.

## Fuentes nuevas verificadas — SHA256

- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-final-c395f5f-three-full-CI-once-low-20261013/final-result.json`: `fbd60a4b53bbe5a3fa6061268274dd1b07e8ff9478507015869c97089cc9a534`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-coverage-only55-prepare-QA-low-20261013/final-result.json`: `046c727bbc633f37ff0163cee96238276d163302d6156cfca5e5d68ebeaef8bd`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-three-approved-focal-blocks-once-low-20261013/final-result.json`: `700a2197d071b183040758f2e9f8774556037bc84cedc03e7afe6c42ee2a2daa`.


---

## Historial documental conservado íntegramente

El contenido siguiente es la fotografía previa del 11 de octubre, preservada sin reescribirla. Sus pendientes y cifras quedan sustituidos donde corresponde por el cierre fechado del 13 de octubre anterior; no describen por sí solos el estado vigente.

# VisualStruct: entrega parcial actualizada para revisión

Actualización documental11deoctubre2026. Proyecto canónico `D:\MisProyectos\Web_VisualEstruct`. Resume evidencia existente: no hay pruebas nuevas, publicación, archivo ni cierre técnico global por actualizar este documento.

## Resultados verificados

**MAX15 nodos está implementado en Grafos y aceptado por QA. Las pruebas funcionales/visuales aceptadas cubren8 nodos.** Fronteras15/16 se validaron sin traza larga, con rechazo sin mutación y conservación de historial legacy. El límite cuenta nodos distintos, no etiquetas. C/H intactos en ese cambio; no se adoptó el candidato privado optimizado. [QA MAX15/casos8,389 hashes](../review-sorting-projection-diff-coverage-quality/evidence/graph-max15-focal8-independent-review/review.md).

| Caso canónico de8 | Espera observada click→cuerpo HTTP/parse/expansión/render final | Resultado aceptado |
|---|---:|---|
| Bellman-Ford |29,473s|Camino1..8/coste7,6011pasos; eventos,ownership,UI/export aceptados.|
| Prim |19,867s|8nodos/7aristas/coste28,3566pasos; aceptación focal.|
| Kruskal |18,016s|Misma topología/coste28,3628pasos; aceptación focal.|

Estas ventanas incluyen preparación visible, no tiempo puroC ni autoplay; no garantizan iguales tiempos para otros grafos ni equivalencia universal8→15. Los antiguos pendientes de implementaciónMAX15 y visualesPrim/Kruskal están resueltos para ese alcance.

DFS, transporte propio yJPG están integrados canónicamente con QA aceptada. La UI fue contrastada con respuesta guardada, sin regenerarDFS30 ni certificar todoslosrenders. RN V3 tiene aceptación finita de cinco reglasRN,BST estricto,padres,ciclos yobjetos vivos compartidos; la reserva histórica de validador parcial está sustituida. [QA integraciónDFS](../review-sorting-projection-diff-coverage-quality/evidence/dfs-transport-jpg-canonical-integration-independent-review/review.md), [adenda RN/criterios18-19](../audit-local-quality-and-unified-controls/criteria18-acceptance-and19-RN-V3-documentary-addendum-low.md).

El smoke final registrado confirmó preview5051 actualizado conMAX15,3902 sesiones originales preservadas byte a byte,15 admitido sin algoritmo largo y16 rechazado antes de ejecución. La cobertura final aceptada en ese cierre fue **20262/24343=83,235427%**,187módulos,4exclusiones existentes ycinco raíces críticas>85%. Es unión compatible de evidencia histórica y cobertura focal nueva, no suite integral recién ejecutada ni cobertura de ramas. **No se atribuye ese porcentaje automáticamente a los cambios o regresiones de9deoctubre.** Criterio18 fue aceptado, pasando a21/22; eso no cierra QA pendiente ni convierte el contador en porcentaje de tiempo. [Handoff final](../audit-local-quality-and-unified-controls/criteria18-19-final-max15-technical-handoff-low.md), [QA final](../review-sorting-projection-diff-coverage-quality/evidence/final-max15-preview-coverage-delivery-independent-review/review.md).

## Dictámenes vigentes:66 IDs originales aceptados finitamente

La indicación anterior de39IDs pendientes está sustituida por los dictámenes fechados. El09octubre, la revisión de esos39 **aceptó27 y rechazó12**: el PASSdelautor no bastaba porque los consumidores permitían corrupciones de proyección pública. El10octubre, la reevaluación independiente **aceptó finitamente los12 reparados**, resolviendo F-01/F-02 en susfixtures. Se conserva el rechazo anterior; no se borra ni convierte retrospectivamente aPASS.

El revisor contrastó **13capturas positivas** (dos inserciones pertenecen aunsoloID) y detectó **879variaciones negativas independientes**, sin corrupciones no detectadas. Son comprobaciones sobre JSONguardado, sin nueva ejecución deproducto,HTTP,C o navegador. LosXMLdelautor registran **12IDsoriginalesPASS y295controlesPASS**, incluidos87negativos; esos87no se suman a879como si fueran la misma campaña. [Dictamen39del09octubre](../review-three-repairs-and-route-consumers/evidence/independent-review/pending39-independent-verdict-20261009.json), [reevaluación12del10octubre](../review-three-repairs-and-route-consumers/evidence/independent-review/rejected12-independent-review-20261010.md).

Balance deluniversooriginal66: **27previos +27aceptadosdelgrupo39 +12reevaluados =66IDsoriginalesaceptados dentro delalcanceprobado**. No son66ejecucionesnuevas, certificaciónuniversaldeoráculos ni cierreglobal. Las39funcionesoriginales yfixtures/históricos se preservaron; no queda pendientes39comoestadovigente deesa revisión.

## Fotografía parcial del10deoctubre, preservada

Elhandoffdel10octubre acredita **474IDsdistintos instrumentadosPASS más1Bellmanexistente reutilizado**,475IDscompletosrepresentados. La cobertura obtenida es **41,233314% parcial (10070/24422líneas)**, con4exclusiones; elgate83%global/85%enloscuatrocomponentes siguependiente/exit1. Sorting8,63%,Graph51,92%,Hash41,86%,Heap38,41%son resultados deestaselecciónparcial, no veredictosderegresiónglobalni medicióncompleta. La cifra83,235427%anterior sigue fechada en su cierre yno se transfiere aesta campaña. [Handoffautor:coberturaparcial](../audit-local-quality-and-unified-controls/evidence/visible-rejected12-tests-remaining-coverage-low-20261010/handoff.md).

Bloque013: exit124 a120,046s,sinXMLnidatodecobertura. Sus28puntosdestdout no son resultadoscertificadosporID ni demuestran tiempoaisladodeuncaso.4889IDsCI aún sin datosinstrumentadoscompletos enesehandoff;122bloquesplaneadossincomenzar. Replanificaciónposterior sólo conresultadoconfirmado; esta actualización no atribuye porcentajes futuros ni resultadosdenuevacampaña.

La única ejecuciónBellmanexistente de440,07s y704,36MiB de memoriaobservada completó elpresupuestoautorizado900s/2GiB; **no se repitió**. Este presupuesto ymedición son deesa ejecución registrada, no SLAusuario ni RAMuniversal; susdatos se reutilizaron únicamente conSHAscompatibles. No sumar preparación,render o campañasdistintas como si fueran unúnico tiempo.

Esa fotografía del10deoctubre queda seguida por la consolidación del11deoctubre descrita abajo; no se reescriben sus resultados. Sigue pendiente el gate global y la entrega final. **La aceptaciónfinita de66IDs no cierra auditoríaglobal,22/22,archivo o publicación.** No se ejecutó ninguna prueba enesta actualizacióndocumental.

## Actualización verificada del 11 de octubre: R3/R4 y cobertura

Se conservan los **66 IDs originales aceptados finitamente** y sus dictámenes fechados. En otro conjunto de reparaciones, R3/R4 tienen aceptación independiente comunicada por coordinación el11deoctubre: **152 IDs únicos PASS =149 reparados +3 regresiones de callers C con peso predeterminado**. No se suman ambos conjuntos como una campaña nueva ni se presume que sean disjuntos. El JSON guardado confirma152IDs distintos y152PASS; R4 revalidó los mismos dos IDs que habían fallado en R3, sin borrar ese resultado anterior. [Resultados porID](../audit-local-quality-and-unified-controls/evidence/visible-directed-mst-consumers-r4-low-20261011/latest-152-unique-case-outcomes.json), [paquete R3/R4](../audit-local-quality-and-unified-controls/evidence/visible-directed-mst-consumers-r4-low-20261011/independent-review-request.md).

La cobertura actual aceptada comunicada por coordinación es **20.029/24.423 =82,008762% (82,01%)**. Los totales coinciden con el reporte estándar guardado. El **gate global83% FALLA**: faltan243sentencias ejecutables distintas para cruzarlo. Los cuatro componentes cumplen85%: **Grafos96,54%,Hash99,22%,Heap92,05%,Sorting92,57%**. No se convierte la cobertura históricaR1/R2 ni el83,235427%delcierreanterior en cobertura actual. Esta consolidación utiliza compatibilidad de fuentes/funciones y datos completos existentes; no ejecutó pruebas nuevas, no añadió exclusiones ni cambió umbrales. [Consolidación y límites](../audit-local-quality-and-unified-controls/evidence/visible-final-static-candidates-consolidation-low-20261011/independent-review-request.md), [reporte de cobertura](../audit-local-quality-and-unified-controls/evidence/visible-final-static-candidates-consolidation-low-20261011/candidate-final-thirty-original-inputs-consolidation-coverage.json), [gate fallido](../audit-local-quality-and-unified-controls/evidence/visible-final-static-candidates-consolidation-low-20261011/candidate-final-thirty-original-inputs-consolidation-gate.log).

Las referencias tituladas independent-review-request son paquetes de solicitud, no el dictamen mismo. La aceptación independiente aquí registrada procede de la comunicación vigente de coordinación; los artefactos enlazados prueban resultados y límites, no sustituyen esa procedencia de aceptación.

### Pendientes y límites que permanecen

- **230 IDs históricos bloqueados por recursos**, JPEG **SKIP** y artefactos temporales privados perdidos se conservan explícitos. No se transforman enPASS, datos de cobertura recuperados o defectos universalmente resueltos. Counting retention-copyERROR sigue documentado.
- El global83% sigue incumplido aunque los cuatro componentes pasen. Hay4394sentencias ausentes en total;243 es sólo la diferencia necesaria para el umbral, no el total de faltantes. La inspección de candidatos restantes no equivale a ejecución ni garantiza recuperar esas243.
- **Reapertura de8IDs cerrados de cola de prioridad pendiente de autorización específica**, decisión yguarda válida. El silencio no aprueba una ejecución nueva. No se ejecutaron esosIDs para redactar o actualizar este documento.
- Bellman900 y sus datos existentes no se repitieron. Los límites120s/2GiB, fuentes, fixtures y resultados incompletos anteriores permanecen; no se amplían recursos o alcance por esta entrega.
- Sigue pendiente la disposición final de cobertura y aceptación/entrega global. No cierre22/22, certificación universalAPI/UI, publicación, commit,push odeploy. La aceptación finita deR3/R4 no cierra automáticamente la auditoría.

## Decisiones y límites

Correctitud,fidelidad y conservación de todoslos eventos/pasos educativos son centrales. Se detienen nuevas optimizaciones por decisión del usuario; no se afirma imposibilidad técnica demostrada. Se permite hasta15nodos, pero pruebas funcionales/visuales actuales sólo8; no prueba larga15 ni repetirBF20/30 por esta entrega.

Sorting no tiene SLA fijo15s. Se distinguen C nativo/intérprete,preparación/validación/transporte yrender/replay humano. Graph15s de ejecución pura permanece no verificado/diferido según disposición aceptada; los tiempos mixtos no pruebanPASS/FAIL y15nodos no significa15segundos. [Decisión temporal](../audit-local-quality-and-unified-controls/criterion18-sorting-informative-three-layer-decision-low.md).

Dijkstra30 privado completo122,546s/22430pasos yBF20 privado1861,922s/60239pasos son evidencia histórica aceptada de versiones privadas, no integración global ni cola obligatoria de pruebas fuera del dominio actual. BF20 tuvo cuerpo176,671MiB, máximo muestreadoPrivateUsage121,574MiB ysesión40→41; no son RAM delnavegador,pico absoluto ni espera humana aceptable. [QA Dijkstra privado](../review-sorting-projection-diff-coverage-quality/evidence/dijkstra-retention-dijkstra30-one180-independent-review/review.md), [QA BF20 privado](../review-sorting-projection-diff-coverage-quality/evidence/bellman-fastpath-textcache20-complete-independent-review/review.md).

ASan/UBSan no enlazables en el toolchain registrado quedan como limitación documentada, sinPASS sanitizado. No garantía universal deinputs,caminos,ABI,UB/OOM,accesibilidad,móvil o todoslosrenders. Criterio14 ya cerrado;11/12/16 aceptados finitamente. C1 mantiene1/12admitido11pendientes, sin nueva admisión por este resumen. El repo cambia durante revisión: cada informe conserva fecha/fuente y no es fotografía atómica permanente.

## Abrir y comprobar localmente

[VisualStruct](http://127.0.0.1:5051), [Grafos](http://127.0.0.1:5051/graph/), [Ordenamiento](http://127.0.0.1:5051/sorting/sorting_array) y[manual](http://127.0.0.1:5051/help/manual). La disponibilidad/version del proceso en este instante no se comprobó de nuevo al redactar.

1. Usa perfil privado para no mezclar tuhistorial; operaciones explícitas modifican esa sesión.
2. Explora entradas pequeñas, hasta8nodos para las comprobaciones funcionales/visuales actuales; no traceslargas15/20/30.
3. Comprueba resultado,líneaC yestado al avanzar/retroceder sin otra ejecución;seekfocal no equivale aautoplay completo ni hooksQA a botones visibles.
4. Consulta ayuda ydescargasC/H/main disponibles; main depende delhistorial. No presentes variantesprivadas como integradas en elpreview.

Documento preparado para revisión del usuario:66IDsoriginales yR3/R4aceptados finitamente,demoras,fuentes,instrucciones ygate global83%fallido explícito. No declara entrega ya realizada ni cierre global.

## Identidad de las fuentes nuevas leídas

- `openspec/changes/review-three-repairs-and-route-consumers/evidence/independent-review/pending39-independent-verdict-20261009.json`: SHA256 `999f320e44605be3672f0c3f3f7e02aac404e07b12b3ee5570831751d695494f`.
- `openspec/changes/review-three-repairs-and-route-consumers/evidence/independent-review/rejected12-independent-review-20261010.md`: SHA256 `e24fb627e423df322a195f2620d0d7f8a69025459d04a83632fba49c6add1f66`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-rejected12-tests-remaining-coverage-low-20261010/handoff.md`: SHA256 `0ec424984c6a0a5e812e36f94b3cec746715f335661f166e2369228dff0dbc67`.

## Fuentes nuevas del11deoctubre — SHA256

- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-directed-mst-consumers-r4-low-20261011/latest-152-unique-case-outcomes.json`: `90cb32f8ab359e1ac2fb2fa35af531a799a887bf966b3755f971954fcc551404`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-directed-mst-consumers-r4-low-20261011/independent-review-request.md`: `a329311955aeacce8add08d86e721be327347d469aea4202d82cfe293790a11d`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-final-static-candidates-consolidation-low-20261011/independent-review-request.md`: `0483ffab598a159afb4e2be3da17e59057e9de25c52a91582f8c531e6436b6a3`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-final-static-candidates-consolidation-low-20261011/candidate-final-thirty-original-inputs-consolidation-coverage.json`: `f2d104d732707bb82315b41943ac62199cfe2204c9227a7311496bf6a193fc5f`.
- `openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-final-static-candidates-consolidation-low-20261011/candidate-final-thirty-original-inputs-consolidation-gate.log`: `fd33858df6d12d41bc1f5e7974b3f55d7dadc1dfd2855e73ae7c0f9e4ac121e6`.
