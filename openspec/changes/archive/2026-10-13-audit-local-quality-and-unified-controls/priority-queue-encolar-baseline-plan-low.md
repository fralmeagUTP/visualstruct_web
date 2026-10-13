# Propuesta de siguiente baseline LOW: Prioridad Encolar

Propuesta, no asignación ni ejecución. Justificación: EncolarCola ya tiene cierre finito; PrioridadEncolar dispone sólo de tests parciales y caller heredado deLimpiar. Su C real añadehelperllamado, campo prioridad/cantidad yretorno bool, por lo que el cierreCola no lo cubre. Registrar nuevaasignación/op/task/binding y before desdeD antes de cualquiercaso nuevo.

Alcance candidato `priority_queue.encolar-baseline-low`, sólo cp_encolar y cp_crear_nodo necesarios. No implementaciónLOW ni otrosmétodos/cierres/C/H/contratos/Graph. Recuperar primero SHAevidencia/tests existentes, incluido `tests/test_priority_queue_trace_conformance.py::test_enqueue_exposes_real_allocator_and_keeps_node_temporary_until_link`; no repetir casos si evidencia vigente cubre el requisito. InventoryIDs único ytests rojos reales sinxfail, sin fijar conteos antes de observarlos.

C actual protegido: bool cp_encolar(ColaPrioridad *cola,int valor,int prioridad), localnuevo declarado indeterminado antesguardacolaNULL; cp_crear_nodo(valor,prioridad) devuelveCPNodo* oNULL, mallocopaco, stores valor→prioridad→sgteNULL, returnnuevo. Luego guarda nuevoNULL; publish delante si vacía/atras->sgte si no vacía, reasignaatras, cantidad++, returntrue. Sinordenarlista alencolar; extracción prioritaria está fuera. Frame porinstrucción, scopes dehelper/parent/caller yretornos bool reales, identidadtemporal/alias hasta scopeexit, contadorsólotrasstore propio; nunca leer campo/puntero indeterminado o retirado.

Fixtures finitos propuestos: vacío, singleton, duplicados/igualprioridad ylímites INT_MIN/MAX devalor/prioridad con cantidad pequeña coherente; dosinserciones cadafixture si permitencompararduplicación/recarga. Faults privados decolaNULL y mallocNULL concontador/roots/heap previos intactos, ownership alfinal ysin éxitosfalsos. NoOOMreal, no payloadUI de fallos, no ejecutar signedoverflow cantidadINT_MAX++ ni fabricarTADinconsistente.

Comparar Cejecutado conPython/API/traza completo: línea/function/calls/returns/guards/scopes/initmask/valor-prioridad-sgte/roots/cantidad/console/ownership. Cnativo seguroinstrumentaCdescargado idénticoD y valida campos sólo despuésstores; comprobar C17 ysinUB. Inventariar C/Hsource200/Doxygen símboloshelpersycallerreal DOM/HTTP porruta existente, sin crearqueue/main oprioritymainendpoint. Mains anteriores deLimpiar no cubren framesEncolar; puedenreusarse sólo si bytes/source/alcancecoinciden.

UI real: dosvistasforward/back conestado/highlight/consola/memoria exactos;4fixtures preparadosrecarga historial+traza+cursor+inputsvalor/prioridad/Siguientereal0POST,5secciones ymodo actual. Priorityfrentehidden no se expone. Recursos8finite si se confirman8acciones: tracemallocPython/respuestabytes/tiempo instrumentado, no RSS/browser/Cheap/SLA/depth/history/OOMclaims. Registrar divergencias/fallos normativos yplanMEDIUM acotado sólo si corresponde.

SalidaLOW: evidencia/hash/testIDs únicos porcaso/checkpoint/beforeafter y hallazgos reales, sin cierre globalniincrementarcontadores/archivar. Requiere coordinación para nuevaasignación antesempezar;baseline no iniciado en consolidaciónEncolar.


## Nueva instrucción vigente

Coordinaciónautoriza ahora ejecutar este baselineLOW. Recuperarevidenciaparcial,guardasallocinit/priorityorderstableties/aliasescontador/pointers/scopes/DOMHTTPcaller/reload,regresionespermanentessinxFail/recursosfinito;planMEDIUMsifallaantesimplementar. C/H/HashSortingRN/apilarencolarlimpiarclosures protegidos,SDDblockedwritesintactos,Graph/Dijkstrapending,nopublish. Propuesta anterior conserva contexto; esta instrucción la habilita sin autorizar implementación.
