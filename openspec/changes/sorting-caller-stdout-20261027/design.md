# Diseño y límites

1. Diagnosticar generador del main, programa de sesión, traza y consola actuales antes de escoger el punto mínimo de integración.
2. Reutilizar el programa/intérprete C existente para evaluar las instrucciones reales de impresión. Los valores y formato deben derivarse de esas instrucciones y su memoria, no de una proyección del estado visual.
3. Registrar la procedencia del caller y su cursor sin atribuirle impresiones al algoritmo silencioso. Conservar los eventos, memoria, estados y contratos pedagógicos existentes.
4. Consultar historial y mover el cursor debe seleccionar evidencia ya producida, sin volver a ordenar ni añadir operaciones.
5. Usar GCC C17 solo como oráculo de pruebas del main/C/H reales; no añadir una dependencia de compilador al servidor.

El backend no modificará JavaScript. Cualquier extensión que necesite interpretación del frontend se comunica a coordinación antes de tocar esa capa. Las pruebas de esta copia no certifican el destino canónico ni un despliegue.

## Implementación elegida

`sorting_caller_console` ejecuta el main generado mediante `Program` y `GraphMachine` existentes, junto con los cuerpos reales extraídos de `arreglo_valido` e `imprimir_arreglo`. La adaptación de ABI sustituye únicamente parámetros C `const int arreglo[]` por su tipo puntero equivalente y el arreglo automático de main por un buffer tipado de ochenta celdas del VM. Los cuerpos, condiciones, bucles y printf siguen siendo los del programa real. El formato se ejecuta con `caller_printf.c_printf`, compartido con coordinación y respaldado por snprintf del CRT/libc, sin formateo numérico Python ni compilador de servidor.

Las llamadas de ordenamiento silenciosas consumen el journal de efectos aceptados, validando algoritmo y memoria de entrada antes de aplicar las celdas de salida. Esto permite GET/reload sin volver a ordenar. Solo existen efectos de runs aceptados; el camino int exitoso corresponde a `ORDENAMIENTO_OK`. Un intento rechazado no se incorpora al programa descargable ni agrega stdout de un caller no aceptado. La copia vacía sin creación aceptada no ejecuta automáticamente el main descargable.

`console_output` representa stdout completo del programa aceptado. `trace.console_prefix` incluye la historia anterior y el header Run ya ejecutado antes de entrar al algoritmo: cursor -1 significa antes del TAD, después de ese header. Los frames TAD intermedios conservan su cantidad, memoria y eventos; permanecen silenciosos. En el último cursor se publica la salida real del caller posterior al retorno, con eventos que identifican main o el helper de impresión; esa agrupación de transporte no afirma que el algoritmo imprima. Las fuentes de páginas se envuelven para conservar el mismo límite en páginas, GET y exportación compacta.
