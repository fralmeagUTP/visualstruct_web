# Inventario accionable de232brechas

Registro original de143vínculos conservado.232pendientes antes/después;0vínculos nuevos:ninguno adicional revisado aquí alcanzó entrada+esperado+contexto completo. No pruebas deaplicación ejecutadas. Cada entrada tiene fuenteinventario,references test/line/hash,tipo evidencia,causa yacción enitems.json/worklist.csv. Lasreferencias son candidatos,no casos certificados.

| Categoría | Total | Acción/operación/ruta referida,contexto sinmapear | Sólo referencia/render | Sin candidato recuperado |
|---|---:|---:|---:|---:|
| Algoritmos |21|21|0|0|
| Controles |139|4|40|95|
| Operaciones |59|59|0|0|
| Fases |4|4|0|0|
| Rutas |9|7|0|2|
| Total |232|95|40|97|

Ausencia real confirmada:0. Duplicados/fueraalcance admitidos:0. Laausencia decandidato porASTliteral no demuestra falta depruebas. MódulosCASES,helpers,fixtureclientalias,cadenas URLs derivadas yselectores dinámicos requieren revisión. Exactas referencias aoperaciones también necesitan asociar estructura/setup/aserción:unliteral no vincula por sísolo.

14entradas llevan flags:12algoritmos degraph comparten implementación encontextos fase distintos;2reset-button tienen mismo selector enplantillas secuencial/jerárquica. No borrar ni restar estas entradas:contextos distintos pueden ser obligaciones legítimas. No identificada exclusión autorizada ni control obsoleto demostrado eneste bloque.

Aceptación pendiente separada:132de143vínculos existentes son sólofuente sin ejecución acreditada enestas fases;11casosexport tienen evidencia de1E2Eprevio. Esto no ordena132ejecuciones:primero asociar evidencia aceptada existente yverificar vigencia fuente/contrato;no repetir campañasconsumidas. Las232sinvínculo requieren mapeo antes de decidir ejecución. No nuevas admisionesC1.

Próximos pasos finitos porgrupo:

1. 59operaciones+21algoritmos:resolver helpers `_post`,tablasCASES yparametrizaciones con datos finitos/aserciones correlacionadas. Priorizar secuenciales `tests/test_comprehensive_sequential_qa.py`,grafos `tests/test_comprehensive_graph_qa.py` yconsumidoresnativos yaacreditados. Distinguir tests de dominio deentradaAPI/trazaUI. No aceptar expectedsuccessgenérico ni fallo proveedor.
2. 7rutas+4fases:resolverclientaliases/fixtures yURLs page_url/export_url;`tests/test_sorting_counting_paging.py` demuestra porqué URLdinámica no equivale afalta test. Hay campañasgrandes históricas:reutilizar evidencia admitida,NOlanzarlas. /sorting/sorting_array yPOST/hierarchical/<structure_id>/reset no tuvieron candidato:revisar helpers/contratos primero,crear casofocal sólo si realmenteausente.
3. 4controles congesto:didactic-mode-switch,export-jpg-scale,hash-reset-button,hier-sim-prev. Casos/source/hash figuranporentrada;completar página,setup,gesto yestadoesperado específicos antes devincular.40referenciasrender no prueban operabilidad:buscar gestos/roles dinámicos odefinir caso si faltan.
4. 95controles sincandidato:reconciliar HTML anónimo/control dinámico conDOM yselectors porrol/texto/clase ya registrados;decidir naturaleza interactiva/contexto antes de escribirtests. No hay autorización dedescartar controles porinvisibilidad estática.
5. Resolver14flags decontexto compartido con decisión explícita:mantener porcontexto salvo justificación verificable decobertura equivalente/exclusión. Sólodespués asignar pruebasfocales necesarias bajo límites establecidos.

ASan/UBSan Pila nuevos completados aparte,no prueban controles niestas232entradas. NoDocker/campaña durante esteinventario,commit/push/despliegue. Registrosanteriores preservados;conteos no porcentaje ni cierre global.
