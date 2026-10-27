# RN-IMPL-01: aclaración documental de comportamiento existente

ID: `rn.validation-contract`
Motivo exacto: RN-IMPL-01: aclarar historial ejecutable de consultas RN preexistente sin cambio de comportamiento ni almacenamiento

Delegación vigente01a0fe61-3104-743a-b032-bcc289ad80cd autoriza releer servicio/RAWtest/contratos y aclarar sólo ambigüedad si conserva comportamiento aprobado. No autoriza nueva conducta, eliminación de consultas, almacenamiento nuevo ni modificación app/audit. Se reabre sólo redacción del contrato previamente cerrado.

Fuente histórica evidence/visible-red-black-query-main-low/README.md registra corrección aprobada de consultas repetidas para caller/reload sin redispatch. hierarchical_structure_service.py:104-112 conserva consultas RN en valid_history sin ejecutar;239-244 añade una entrada de la consulta completada. test_rbt_full_validator_raw_service.py:16 exige history+[validar] para False ejecutado exitosamente.

Conclusión: distinguir efecto mutante estructural de registro ejecutable de consulta. History RN actual es registro cronológico que puede contener ambos; no se presume journal separado ni esquema nuevo. Validar no cambia valores/colores/enlaces/reservas ni añade efecto mutante; la ejecución explícita completada se registra una vez, inclusoFalse; navegación/reconstrucción no añaden ni reejecutan consulta. El texto previo «no muta historial» era demasiado amplio y no debe usarse para borrar conducta previa. Spec session-state sigue hablando de historial mutante: registrar divergencia de descripción general, no reescribirla ni elegir contrato global desde esta aclaración RN. Grafos/Dijkstra/C1 sin cambios.
