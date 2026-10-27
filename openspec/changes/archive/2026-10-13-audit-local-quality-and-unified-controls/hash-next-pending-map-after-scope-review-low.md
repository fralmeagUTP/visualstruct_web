# Mapa Hash pendiente tras revisión LOW

H1 ya aprobado: intC/capacidad fija/encadenamiento. No redecidir contratos. Creación/inserción siguen sin cierre por dos hallazgos de tipo/scope dentro de casos finitos; corregir y consolidar primero. El inicio del siguiente baseline está condicionado por la instrucción nueva a ese cierre, aún no ocurrido.

| Métodos pendientes | Baseline propuesto | Dependencias/límites |
|---|---|---|
| get / contains | Primero, consultas vacía/presente/ausente, cabeza/medio/cola, negativas y extremos; puntero de salida, dummy_valor, relación contiene/buscar; C real/trace/UI/caller | H1 estable. Contrastar get ausente con spec vigente antes de tocar servicio. No volver a auditar implementación cerrada de create/insert como cobertura nueva; fixtures de estado pueden usarla después de cierre. |
| remove | Vacía/ausente/cabeza/medio/cola, enlace anterior, free, cantidad-- | Ownership/identidades y errores; conservar contratos de int/capacidad. |
| keys / values / items | Órdenes por buckets/cadenas, duplicación de valores y formateo C/buffer | No asumir equivalencia de orden/cadenas ni truncación sin ejecutar C. |
| stats | Vacía/colisiones/carga>1 y precisión floatC vsPython/visual | Capacidad fija; tolerancia apoyada en float real, no ajuste semántico. |
| clear / destroy_table | Cleanup, contenido/capacidad/punteroNULL, reinicialización explícita y repetición | Distinguir conservación de buckets en clear y liberación en destroy. Guardas C y caller; no contar cleanup de caller como cierre de ambos métodos. |

Nueve métodos =2consultas+1remove+3listados+1stats+2lifecycle. El agregado Hash/global permanece abierto. No cambios RN/Grafos ni repetir once cierresSorting.
