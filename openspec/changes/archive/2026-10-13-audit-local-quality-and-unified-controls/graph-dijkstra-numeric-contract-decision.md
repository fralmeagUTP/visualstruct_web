# Decisión pendiente: contrato numérico de Dijkstra

Este bloque LOW corrige únicamente el historial y el programa generado. No cambia el algoritmo C, los cálculos del backend ni la política decimal. La evidencia está en `evidence/visible-graph-dijkstra-history-caller-low`; el baseline nativo anterior conserva los 16 casos y sus resultados.

## Conducta actual, alternativas y recomendación

| Tema | C descargado | Backend/API actual | Alternativas mínimas | Recomendación |
|---|---|---|---|---|
| Empates | Gana el primer índice de la lista de vértices; una distancia igual no sustituye al predecesor. Caso: camino 1–3–4, costo 2. | La selección desde un conjunto produce 1–2–4, costo 2. | A: alinear Python y traza con el orden C. B: cambiar C y documentar otra regla. | A: mismo C que aprende el estudiante. |
| Infinito `INT_MAX` | Un costo igual a 2147483647 no reemplaza el valor inicial infinito; retorna NULL. | Publica un camino de costo 2147483647. | A: conservar el límite C y explicarlo. B: ampliar tipos o redefinir el infinito en C. | A dentro del contrato actual. |
| Suma fuera del rango | Comprueba `dist[u] <= INT_MAX - costo` antes de sumar. El caso `(INT_MAX-1)+2` retorna NULL. | Publica costo 2147483648. | A: reproducir la guarda C. B: ampliar representación y guardas nativas. | A. El caso C observado está definido; no ejecuta una suma desbordada. |
| Pesos fraccionarios | `NodoA.costo` y el argumento son `int`. | Rechaza 2.5 y "2.5" con HTTP 400; acepta 2.0 como entero. La spec canónica aún exige aceptar 2.5. | A: reconciliar la spec con API/C enteros. B: diseñar pesos decimales en C, algoritmos, trazas y descargas. | A respeta el producto actual y el C docente; necesita decisión explícita sobre la spec. No truncar silenciosamente. |
| Pesos fuera del rango C | El argumento `int` no representa 2147483648 ni 1e40. | Acepta 2147483648, -2147483649 y 1e40, aunque su mensaje habla de un entero representable. | A: validar finitud, integralidad y rango C, con serialización segura. B: ampliar tipos nativos y parser/exportación. | A: hacer cumplir el contrato declarado; autorizar su alcance en la validación compartida. |
| Valores no finitos | No son entradas válidas para el oráculo entero propuesto. | Infinity causa HTTP 500 por `OverflowError`; NaN devuelve HTTP 400. | A: rechazar limpiamente antes de convertir. B: introducir otro contrato. | A; el HTTP 500 es un defecto de validación, no un resultado válido de Dijkstra. |

Propongo aprobar un paquete coherente: conservar la representación nativa entera; alinear empate, infinito y guarda de suma con ese C; rechazar valores no finitos o fuera del rango; reconciliar explícitamente el requisito decimal. Se mantiene el rechazo actual de fracciones. La construcción puede seguir admitiendo arcos negativos para otros algoritmos, pero Dijkstra rechaza cualquier arco negativo, incluso desconectado del inicio.

Si se desean distancias más amplias o pesos decimales, conviene una especificación separada que cambie los tipos y sus efectos en todos los algoritmos, archivos C/H, trazas, mensajes y programas generados. No elegir esa ampliación durante la corrección de fidelidad.

## Conducta definida y comportamiento indefinido (UB)

Los 16 casos nativos usan pesos representables. `INT_MAX` como infinito y la suma descartada por la guarda son resultados definidos. Un desbordamiento aritmético con signo sin protección sería UB; este baseline no lo ejecuta.

La API aceptó 1e40. El generador real produce `g = grafo_insertar_arco(g, 1, 2, 1e+40);`. Al convertir ese `double` a `int`, su parte entera no es representable: ejecutar esa conversión implica UB. No se ejecutó ese programa ni se usó como oráculo. Las comprobaciones de sintaxis C17 de GCC 15.2, incluso con `-Wfloat-conversion`, no lo advirtieron: compilar no demuestra corrección.

Para el literal entero 2147483648, la conversión fuera del rango a `int` con signo depende de la implementación o de una señal definida por ella; no se clasifica automáticamente como el mismo UB de la conversión flotante. GCC lo rechaza con los flags estrictos. No se toma su valor convertido como un peso portable válido.

Una fracción flotante representable se trunca hacia cero al convertirse a entero: puede estar definida y aun así incumplir un contrato decimal. Actualmente la API rechaza esas fracciones. Se corrigió la afirmación anterior del manual que confundía la spec decimal con la conducta actual, tras 11 observaciones reales de entradas.

La clasificación de conversiones y aritmética se apoya en [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), §§6.3.1.3, 6.3.1.4 y 6.5p5, borrador público del comité. Las comprobaciones del compilador se ejecutaron en modo C17. No se atribuye un resultado de ejecución a ningún programa con UB.

## Verificación después de decidir

Conservar las tres regresiones numéricas fallidas hasta verificar la corrección elegida. Si se aprueba A, añadir entradas de rango/no finitas/fraccionarias y serialización C; mantener el oráculo de empate, infinito y guarda. No ejecutar conversiones inseguras como casos válidos.

El bloque MEDIUM propuesto observará arreglos `int`, orden de índices, condiciones, llamadas y memoria antes/después. Debe eliminar la narración genérica de distancias `double` y cola de prioridad cuando no corresponde al C. El programa generado ya imprime el resultado C y libera sus arcos; conserva la ambigüedad de NULL entre camino sin arcos, falta de ruta y errores de entrada/memoria. No se simulan fallos de reserva en los casos normales.

BFS/DFS siguen cerrados para sus casos registrados. Global: 13/22; documentación: 105/208. No se implementó política numérica ni decimal en este bloque; sin push, merge o despliegue.


## Confirmación nueva 2026-10-03: enteros y reglas actuales C de Dijkstra

Usuario confirmó pesos enteros representables y reglas C actuales de Dijkstra. Esta instrucción sustituye las filas históricas que aún pedían decisión de enteros/decimales y de empate/INT_MAX/guarda Dijkstra. Ver graph-approved-integer-dijkstra-contract-decision-low.md y specs/graph-structures/spec.md. No implementación/paridad técnica cerrada; representación/ciclos Bellman-Ford y dominio Prim siguen pendientes por su propia decisión. No volver a preguntar pesos/Dijkstra ni ampliar automáticamente su restricción no negativa a otros algoritmos.
