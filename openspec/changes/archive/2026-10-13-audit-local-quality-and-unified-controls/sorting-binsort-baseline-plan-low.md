# Binsort: siguiente baseline LOW preparado

Preparado por revisión Counting autorizada; PLAN, no ejecución ni implementación. Proyecto D:\MisProyectos\Web_VisualEstruct. Operación futura sorting.binsort-baseline-low; debe recibir assignment_source coincidente y guarda before. No seleccionar siguiente operación desde un checkpoint ni reabrir Counting.

## Fuente y pregunta causal

C/H vigentes: ordenar_binsort(int[],size_t) retorna ordenar_counting_sort(arreglo,n) exactamente. Conserva status/rango/calloc/free del delegado; no usa una estructura independiente de buckets. Python _run_binsort todavía invoca la ruta heredada _run_counting_sort con frames agregados; inspección estática sólo, todavía no baseline ejecutado ni defecto declarado cerrado. La ayuda anuncia delegación y el caller usa retorno int.

## Alcance del baseline

1. Fotografía D de adapter/domain/help/template/main y C/H; proteger hashes de los nueve métodos cerrados. Documentar source extraction incluyendo wrapper y delegado. No ejecutar suites standalone de esos métodos.
2. Observar C17 estricto el wrapper Binsort, llamada y retorno/status; reutilizar resultados/oráculos Counting para el cuerpo delegado cuando sus bytes/datos coincidan. Diferenciar eventos nuevos del wrapper de eventos heredados, sin contarlos dos veces como cobertura.
3. Con pocos casos causales: singleton7; normal[3,1,2]; negativos/duplicados[-3,-5,-3,-4]; outside4[5,4,3,2,1]; k6[0,5]; rango rechazado[0,1000000]. Añadir NULL/n0 y callocNULL aislado como probesC fueraUI/simulados, con status/memoria/input. No fullspan32bit ni OOMglobal ni streams máximos nuevos sin causa: límites/encoder Counting ya verificados.
4. Baseline API/UI/main reales con selección Binsort, repetición, error, reload/replay/JSON/5secciones y descargasC/H. Compilar main original C17/Doxygen y observar ownership sin sustituir main por variantes. Contrastar resultado y métricas con delegación real, trazas wrapper/helper/locales/source. Mantener contrato de retorno y límite vigente.
5. Registrar regresiones causales permanentes donde falte instrucción; no xfail/debilitar asserts. Corregir sólo defectos LOW inequívocos de historial/caller/rotulado si existen. Si falta adaptación compleja de trace/player para wrapper paginado, presentar diseño y alcance MEDIUM antes de implementarlo; no duplicar intérprete ni reabrir cuerpo Counting por rutina.
6. Cerrar evidencia baseline, actualizando sólo Binsort propio y pasando after. La sintaxis verde no cierra método. Preview5051 único verificado antes de tocar; sinpush/merge/deploy/red.

## Entregable y criterio

Informe pequeño que distinga delegado ya verificado, comportamiento nuevo observado del wrapper, diferencias reales y regresiones. Estado inicial Binsort pendiente; Counting9/11 no equivale a Binsort10/11. Paso a MEDIUM sólo si el baseline identifica un hueco concreto; no expansión por formalismo ni ejecución de métodos cerrados.
