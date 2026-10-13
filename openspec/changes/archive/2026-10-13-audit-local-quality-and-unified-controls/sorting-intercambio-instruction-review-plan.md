# Siguiente bloque propuesto: Intercambio por instrucción

No ejecutado. Requiere asignación fina `sorting.intercambio-instructions` y guarda before propia. Si la instrumentación requiere mayor razonamiento, proponer MEDIUM acotado para este bloque y terminar su transferencia para volver LOW. No instrumentar once métodos simultáneamente.

## Oráculo reusable
Descargar C/H reales y registrar hashes. Instrumentar `ordenar_intercambio`, `arreglo_valido` e `intercambiar` sin reimplementar el algoritmo. Capturar cada instrucción ejecutada con función/línea, antes/después, tipos int/size_t, punteros al arreglo del caller, alias a/b, temporal, i/j/n, condición, iteración, escrituras y retornos. Registrar comparaciones verdaderas y falsas. Separar rechazo API de guarda NULL/n=0 nativa. Resultado ordenado no sustituye una traza causal independiente.

## Seis casos finitos
Un elemento; dos ascendentes; dos inversos; duplicados sin intercambio; [-3,0,-1,0]; extremos int en tres posiciones. Máximo cuatro elementos, memoria normal. Registrar las tres escrituras del swap y su estado parcial, sin anticipar el resultado. Duplicados int no observan estabilidad de identidades.

## Contraste y replay
Frame inicial antes de llamar; resaltado significa instrucción recién ejecutada. Contrastar arreglo, temporales, scopes, línea, condición, stack, eventos y métricas con vista de arreglo y estrategia reales. No inventar vista enlazada inexistente. Next/prev/seek y cambios de modo sobre la misma traza deben restaurar el frame exacto sin POST, nuevo run ni salida futura. API step usa la entrada original del último run; una creación/selección posterior prepara otra ejecución. Contar entradas únicas; estados de replay no son casos adicionales.

## Main ausente: alcance separado
La UI actual no genera main. Coordinar su implementación antes de atribuir callers C17 reales: materializar create/random, preservar runs cronológicos sobre el arreglo actual, manejar retornos void/int, imprimir resultados C y definir ownership. Compilar el programa realmente mostrado con C/H HTTP, Doxygen y observador independiente. Los 110 fixtures equivalentes del baseline no sustituyen ese main del producto.

## Cierre y límites
Exigir una fila por instrucción nativa ejecutada, frames y métricas sin anticipación, aliases y retornos correctos, fallos excluidos del historial, evidencia C17/Doxygen y guardas before/after. Cierre sólo de Intercambio para casos registrados. Los otros diez métodos, utilidades documentales, main ausente y decisiones numéricas de Grafos siguen abiertos. Sin commit, push, merge ni despliegue.
