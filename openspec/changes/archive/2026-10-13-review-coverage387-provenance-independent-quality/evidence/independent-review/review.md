# Dictamen independiente: procedencia y recombinación cobertura387

**Aceptada la procedencia y recombinación del paquete congelado de387IDsPASS.** La unión reproducida es18852/24154=78.0491844%,186módulos y4exclusiones. Gate83 **FAIL**,1196líneas adicionales hasta el mínimo entero del umbral. Este dictamen no incluye405, no certifica fidelidad universal ni cierraQA18/global.

## Verificaciones independientes

Manifiesto SHA `079778bd62f87cd31a11396f22c39984e3b3ea669b167373f0d5932887bbfe95`;369referencias comprobadas porSHA entre originales canónicosD y copias congeladas, con tamaños. Los186SHAapp coinciden con el destino y con las diez fotografías. El conjunto coincide con todos los archivosPython actuales deapp, sin recortar módulos por porcentaje. Runtime vincula los tests realmente seleccionados a susSHA actuales; los changes de test anteriores no se propagan a ejecuciones que no los recogieron. La evidencia runtime contiene un marcador genérico SortingInterpreter; por sí solo no demuestra todos los imports. El destino se sostiene además en cwd/PYTHONPATHdelrunner, rutasD de raw y fuentes/fotografías verificadas.

Comprobé selección/colección, IDs deXML y eventos setup/call/teardown: exactamente387PASS únicos, sin fallos, skips, timeouts ni duplicados. Los grupos son193+34+6+29+19+22+20+24+20+20. Evidencia por grupo (evidencia local: `openspec/changes/archive/2026-10-13-review-coverage387-provenance-independent-quality/evidence/independent-review/provenance-independent.json`).

| Ejecución congelada | IDsPASS | IDs con contexto app medido |
|---|---:|---:|
| visible-stable193-current-coverage-low | 193 | 193 |
| visible-sorting-semantic-gap-low | 34 | 34 |
| visible-global-consumer-group-plan-low | 6 | 6 |
| visible-global29-five-oracles-repair-low | 29 | 29 |
| visible-rbt19-current-cache-focal-low | 19 | 19 |
| visible-avl-delete-focal-current-low | 22 | 22 |
| visible-heap20-four-instruction-modules-low | 20 | 20 |
| visible-sequential24-current-consumers-low | 24 | 13 |
| visible-rbt-query-clear20-current-low | 20 | 2 |
| visible-avl-abb20-current-low | 20 | 8 |

Los41IDs sin contextoapp individual pertenecen a los tres últimos grupos. Los fixtures de módulo construyen trazas con producto actual bajo setup del primer parámetro y los casos siguientes comparan las trazas compartidas contra oráculos. XML/eventos acreditan susPASS; no se inventan contextosrun o líneas por cadaID. Los346IDs con contexto no son346pruebas independientes de cada rama. Esto limita atribución por parámetro, no invalida la unión de líneas observadas. Preparación nativa, números de eventos y fixtures no se suman como IDs.

## Recombinación y configuración

Preparé copia privada delverificador con cambios exclusivamente en rutas de paquete/output; el original y su author-recombine-check quedaron intactos. Su resultado mecánico conserva la etiqueta autor heredada; **el dictamen independiente es este documento**, no esa etiqueta. Diff de rutas (evidencia local: `openspec/changes/archive/2026-10-13-review-coverage387-provenance-independent-quality/evidence/independent-review/verifier-path-only.diff`), recombinación privada (evidencia local: `openspec/changes/archive/2026-10-13-review-coverage387-provenance-independent-quality/evidence/independent-review/recombined/recombined.json`).

Sin importar producto ni arrancar cobertura, recombiné los diezraws en carpeta propia y comparé por módulo executed_lines,missing_lines,excluded_lines,summary ytotales: igualdad exacta con la unión publicada. Comprobación adicional independiente medianteSQLite read-only: OR de bits por archivo/contexto de los diezinputs coincide con raw publicado y raw privado, pese a que SHA del archivoSQLite puede variar por orden de inserción. Coverage7.14.0/branchFalse coinciden; raw sólo contiene rutas canónicas dentro deapp. No se cambia exclusión/config para alcanzar elgate:pytest.ini congelado es idéntico alactual y la recombinación sinconfigespecial reproduce las cuatroexclusiones y denominador completo.

## Fuente nativa y selección corregida

Contrasté mapas de fuentesC/H/observers/tests de bindings nativos conSHAactuales. RNdelete conserva la tripleta C/H/observer declarada en reviewcache; AVLdelete conserva inputs,reviewSHA yC/H descargados exactos. Los cuatro reportesHeap y susC/H coinciden conbindings; reportesRNquery/clear yAVL/ABB están ligados porSHA. Los plugins leídos aplican guards de fuentes/reportes y reconstruyen trazas del producto actual bajo cobertura antes de compararlas. No ejecuté compiladores ni regeneré oráculos. Algunos reportes son referencias externas canónicas SHA-bound, no copias autocontenidas delpaquete; sus identidades comprobadas quedan en evidencia propia. La aceptación exige conservar también esas referencias para reproducción posterior.

El grupo29 es la corrida corregida con testSHA aceptado enQA5focal. XML/eventos/fuentes la distinguen de la corrida mixta24PASS/5FAIL, aunque ambosraws pueden tener los mismosbytes porque las aserciones no cambian las líneasapp. No se usaSHAraw para inferirPASS ni se cuenta la corrida mixta además de la corregida. Elraw combinado independiente tiene exactamente los contextos/líneas de los diezinputs seleccionados; no incorporaBFSprototipo, campañas históricas o405.

## Alcance final

Aceptación de evidencia de ejecución y unión de cobertura de líneas, no revisión semántica exhaustiva de387tests, cobertura de ramas/inputs universal, performance,Doxygen, replay o decisionesRN pendientes. Fuentes y contratos vigentes preservados; copias no sustituyen evidencia deldestinoD. No se ejecutópytest/native/browser/benchmark ni una campaña de cobertura. Sólo lectura,recombinación privada y evidencia/tracker propios, guardasbefore/after; sin producto,Git,preview o despliegue.
