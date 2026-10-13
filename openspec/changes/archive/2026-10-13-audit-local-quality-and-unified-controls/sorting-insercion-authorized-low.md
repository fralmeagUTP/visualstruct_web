# Instruccion vigente: Insercion LOW baseline y preparacion

Asignacion coordination-sorting-insercion-baseline-low-20261002; operacion sorting.insercion-baseline-low; nueva coordinacion explicita 2026-10-02. Consolidar Seleccion por lectura de cierre/evidencia/hash, sin repetir su caso cerrado; conservar historicos y assignment anterior. Intercambio/main y Seleccion cerrados solo casos registrados, no cierre global.

Preparar Insercion existente: seis entradas <=4 [7],[1,2],[2,1],[2,2],[-3,0,-1,0],[INT_MAX,INT_MIN,0] y guardas n0/NULL separadas del rechazoAPI/UIvacio. Baseline independiente sobre C descargado, observar comparaciones, cortocircuito j>0, desplazamientos, clave int, i/j size_t y scopes; contrastar resultado/status y frame actual, main real/historial/recarga. Reusar extractorC y audit_program caller, no repetir once metodos ni suite cerrada. Documentar resultados y regresiones permanentes sin xfail para fidelidad pendiente.

Implementar si es alineacion sencilla LOW; si exige nuevo contrato de eventos/scopes/cortocircuito y UI reversibles, delimitar MEDIUM con fuentes/casos/criterios concretos; no declarar fidelidad por resultado. Preparacion MEDIUM no autoriza ejecucion futura sin coordinacion fina. C/H algoritmos y numericosGrafos intactos, cinco secciones/5051, docs121/208 y global13/22 conservados; sin push/merge/despliegue.
