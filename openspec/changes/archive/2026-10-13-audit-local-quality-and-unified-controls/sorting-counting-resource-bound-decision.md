# Counting sort: alcance de snapshots por instrucción

Asignación vigente coordination-sorting-counting-medium-20261002, autorización MEDIUM acotada al plan/seis casos. La inspección del nuevo recorder detectó que cada evento copiaría kfrecuencias y que los controles del for de reconstrucción generan O(k)eventos: memoria O(k²), inapropiada para k=1000000 ya aceptado. No ejecutar ese recorder sobre capmillón ni cambiar silenciosamente el contrato/rango.

Decisión rutinaria de implementación dentro del alcance acotado: opt-in Counting por instrucción solo n<=4 yk<=4. Los seis casos autorizados cumplen. Fuera de ello, se conserva implementación agregada LOW (incluye métricas corregidas, rawconsole yvalidación de rango vigentes). Siguen aceptados hasta80elementos yk<=1000000; rechazo rango grande antesreserva siguecomoantes. C/H ydefault/Binsort/Radix no se modifican.

Un test adicional independiente bloquea la llamada al recorder completo fuera del alcance, valida dos entradas pequeñas fuera de n/k con resultado/métricas ycomprueba despacho del caso capmillón mediante stub agregado sin reservar ni generar traza grande. No es casoC/UI nuevo ni prueba de fidelidad de entradas amplias.

Límite: ampliar cierre de instrucción a dominio completo requiere recorder escalable con diferencias/snapshots acotados y coordinación posterior; esta decisión conserva conducta funcional previa, no resuelve su fidelidad. size_t64 siguecondición deloráculo; variante32bit insegura no ejecutada ni contratoC cambiado.


## Decisión posterior aplicable

La instrucción nueva de revisión LOW ysorting-counting-scope-correction-decision.md superan la interpretación de este corte como solución suficiente. Se reconoce protección temporal pero Counting permanece parcial para entradas admitidas. Esta decisión histórica se conserva; implementación no alterada durante diagnóstico. Plan ampliado sorting-counting-expanded-fidelity-plan.md requiere coordinación antes de cambio complejo.
