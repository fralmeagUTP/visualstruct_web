# VisualStruct · Manual para estudiantes

Actualizado el 27 de octubre de 2026. En la aplicación, abre **Manual** (`/help/manual`) para usar los enlaces y desplegar la referencia avanzada. Este documento explica el mismo flujo sin necesidad de recorrer el código del proyecto.

## Empieza aquí: una práctica de 5 minutos

**Reto: ¿por qué una pila es «último en entrar, primero en salir»?**

1. Abre Secuenciales → Pila. Parte de una pila vacía; exporta tus datos antes de Restablecer TAD si tienes trabajo que conservar.
2. Abre **Agregar varios**, escribe `10, 20, 30`, revisa el orden y pulsa **Cargar valores**.
3. El tope será 30. Predice qué valor saldrá primero.
4. Elige **Desapilar**, activa **Paso a paso** y ejecuta. Avanza con **Siguiente paso**: observa el cambio de tope y la liberación del nodo.
5. Al final quedan 20 y 10. En Resultados → **main.c del historial**, observa que la carga hizo tres llamadas normales.

¿Y en una Cola? Saldría primero 10. Prueba el mismo ejemplo para comparar LIFO (último en entrar, primero en salir) con FIFO (primero en entrar, primero en salir).

## Acomoda la vista

La cabecera compacta deja espacio al gráfico y al C, juntos en la vista de clase. En pantallas estrechas los paneles se reorganizan.

- **− / +** alejan/acercan el dibujo; **100%** recupera su escala inicial.
- **Encajar vista** intenta ajustar el contenido manteniendo texto legible. Si no cabe, desplázate con las barras del dibujo: no se eliminaron nodos.
- **Centrar inicio** vuelve al inicio del área desplazable, sin cambiar zoom ni datos.
- Zoom y desplazamiento se conservan durante los pasos de esa vista; no necesitas encajar cada vez.
- **Memoria y reservas · abrir / cerrar** muestra detalles auxiliares disponibles. Empieza cerrado y abrirlo no ejecuta operaciones.
- En **Comprender**, lee primero las tres pistas contextuales: qué ocurre, qué cambia y qué comprobar. La referencia y el detalle avanzado son opcionales.

## Ejecutar no es lo mismo que reproducir

**Normal:** ejecuta y muestra el resultado final. Úsalo para preparar datos o comprobar respuestas.

**Paso a paso:** actívalo antes de ejecutar. Paso 0 representa el inicio. Paso anterior/Siguiente paso revisan una misma llamada; la línea C resaltada acaba de ejecutarse y el dibujo muestra su efecto. Una condición o retorno pueden dejar intactos los nodos.

- **Ejecutar operación** inicia una llamada nueva.
- **Reproducir / Pausar** controlan la reproducción de la traza, no deshacen el TAD.
- **Cerrar paso a paso** muestra el final de esa misma operación, sin repetirla. Reactivarlo permite revisar una traza conservada; no fabrica una traza ausente de una ejecución normal.
- **Restablecer TAD** (o **Reiniciar**, según el módulo) borra la estructura y el historial de esa sesión; no equivale a volver al primer paso. Exporta antes lo que quieras guardar y lee cualquier confirmación.

## Agregar varios

Disponible en **Pila, Cola, Lista enlazada, Lista circular, ABB, AVL, Rojo-Negro y Montículo binario**. Las listas insertan al final. Grafos, Hash, Cola de prioridad y Sublista no tienen carga múltiple; Ordenamiento mantiene su propia entrada de arreglo.

1. En Preparar, abre **Agregar varios**. Introduce hasta **50 enteros** separados por comas: `8, -3, 12`. Admite espacios exteriores y signos. No admite decimales, posiciones vacías ni coma final. Rango: −2147483648 a 2147483647.
2. Revisa cantidad y orden. Se valida toda la lista antes de enviar el primer valor. **ABB, AVL y Rojo-Negro rechazan duplicados**, tanto dentro del lote como respecto al árbol actual. Pila, Cola, listas y Montículo los permiten.
3. **Cargar valores** agrega en orden en modo normal. **Agregar paso a paso** prepara la primera inserción para estudiar su traza.
4. Usa los controles propios del lote. **Reproducir traza** recorre sólo el valor actual. Al final pulsa **Siguiente valor** para aceptar el siguiente; al terminar el último usa **Finalizar lote**.

Después de terminar o detener un lote, **edita la lista antes de iniciar otro**. La vista previa conserva el orden solicitado; el resumen del lote deja de aplicar después de una operación individual o Restablecer TAD.

**Detener lote** conserva lo ya aceptado, incluida la operación actual, y descarta pendientes. No es una transacción que se deshace entera. Ante un fallo durante la ejecución, las operaciones anteriores permanecen. Si una petición queda con resultado incierto, pulsa **Recargar estado e historial** y comprueba lo guardado; no reenvíes a ciegas.

## Lee los resultados y guarda tu práctica

| Panel o control | Para qué sirve |
| --- | --- |
| Consola C (printf) | Salida realmente impresa por C. Puede estar vacía en una operación correcta. No confundir con avisos de la aplicación o diagnósticos de error. |
| main.c del historial | Programa principal con las llamadas registradas; no es la consola ni el cuerpo de una sola función. |
| Estructura del TAD | Tipos y campos de C que representan los datos. |
| Copiar C / Copiar salida | Copia fuente sin números de línea / texto de consola. |
| Ampliar / Cerrar ampliación | Más espacio para leer y regreso a la vista sin ejecutar. |
| Exportar JPG | Imagen para informes; calidad/escala no cambian los datos. La exportación completa no se limita al recorte visible por zoom. |
| Exportar JSON / resumen | Datos o resumen indicado en el control. No es C ni implica que exista importación. |
| Fuente .c y encabezado .h | Descargas completas en la ayuda de cada TAD. Son bibliotecas, no un main. |

Copia el main desde Resultados o usa la descarga directa donde se ofrezca. Compílalo con el C/H correspondiente. Si el navegador bloquea Copiar, selecciona el texto manualmente o descarga la fuente.

## Guías por familia

### Secuenciales

- Pila: tope y orden LIFO; Cola: frente/final y FIFO.
- Lista enlazada/circular: prueba valores repetidos, búsqueda y borrado. Agregar varios inserta al final. La lista circular debe cerrar el anillo al terminar; durante una escritura puede verse un estado transitorio.
- Cola de prioridad: se atiende el menor número de prioridad; empates por llegada. La cadena física conserva el orden de llegada.
- Sublista: distingue padre e hijo. Las operaciones buscan la primera coincidencia; eliminar un padre libera antes sus hijos.
- Lista: Buscar elemento informa todas las coincidencias; Eliminar repetidos elimina todas las ocurrencias del valor indicado. Las posiciones de la interfaz empiezan en 1.

Ayuda: `/help/sequential`, y la guía específica desde su tarjeta.

### Árboles y montículo

Agrega `30, 20, 10` en un ABB vacío y luego en un AVL vacío. Observa la diferencia de forma y la rotación. ABB, AVL y Rojo-Negro mantienen orden estricto sin duplicados. El balance o los colores pueden pasar por estados transitorios durante una operación; comprueba las reglas al final.

El Montículo es mínimo: la raíz es el mínimo, pero su arreglo no está ordenado globalmente. Admite repetidos. Validar Rojo-Negro con resultado falso es una consulta completada, no una entrada inválida; valida, no repara el árbol. En AVL, el factor es altura(derecha)−altura(izquierda); la validación auxiliar por alturas no certifica todos los campos almacenados.

Ayuda: `/help/hierarchical`.

### Grafos

Crea un grafo no dirigido con vértices 1, 2, 3 y aristas 1–2 de peso 4, 2–3 de peso 2 y 1–3 de peso 9. El camino mínimo 1→3 pasa por 2 y cuesta 6. BFS busca por capas, no por suma de pesos.

- Usa Construcción, Recorridos, Camino mínimo y Expansión mínima según la pregunta.
- Identificadores y pesos son enteros de 32 bits. 2.0 se normaliza a 2; fracciones y valores fuera de rango se rechazan.
- Máximo visual: 15 vértices. Empieza con 3 o 4 para seguir fácilmente las instrucciones.
- Dijkstra rechaza pesos negativos, incluso desconectados. Bellman-Ford detecta ciclos negativos alcanzables.
- Prim y Kruskal requieren conexiones simétricas y conectividad en el grafo no dirigido. Un grafo desconectado no devuelve un bosque exitoso.
- Una traza admite hasta 4.000 eventos C/llamador más la publicación final. Si supera ese presupuesto se rechaza su preparación, sin truncarla. Reduce el ejemplo o usa modo normal para obtener el resultado completo sin guardar esa traza extensa.
- Historiales del contrato anterior se conservan suspendidos, no vacíos. Expórtalos antes de confirmar Restablecer datos; no se reinterpretan silenciosamente.

**Referencia avanzada:** el C sigue el código del libro. `GrafoEstado` distingue OK, MEMORIA, NO_EXISTE, PESO_NEGATIVO, CICLO_NEGATIVO, DESCONECTADO, ARGUMENTO y RANGO. NULL no basta para concluir error: un camino de un vértice a sí mismo puede tener cero arcos y estar bien. Distancias `long long` y marca alcanzable son independientes; INT_MAX no es infinito. Eliminar vértice elimina sus arcos incidentes dentro del C. Las listas de vértices/arcos consultadas son prestadas; resultados propios se liberan con la función correspondiente. El modo no dirigido hace una llamada por sentido: si falla la segunda, no deshace la primera.

Ayuda: `/help/graph`.

### Hash

Crea capacidad 5; inserta clave 1, valor 10 y luego clave 1, valor 20. Al consultar obtendrás 20 y una sola entrada.

Claves y valores son enteros de 32 bits. Capacidad visual: **1 a 128 buckets**, fija, sin rehash automático. Una colisión encadena claves distintas. Vaciar conserva los buckets; destruir libera también ese arreglo. Las sesiones antiguas que superan el límite quedan suspendidas y exportables antes de restablecer, no recortadas. Este límite es del visualizador, no una garantía de memoria para cualquier capacidad del TAD C.

Ayuda: `/help/hash`.

### Ordenamiento

Usa `4, 1, 3, 2` y compara Burbuja e Inserción, recreando la misma entrada inicial. Se admiten **1 a 80 enteros int32** y once métodos. Predice comparaciones, movimientos e intercambios antes de avanzar.

Counting y Binsort requieren rango inclusivo máximo−mínimo+1 ≤ 1.000.000; no es la cantidad de elementos. Binsort delega en Counting. Los métodos que devuelven estado usan `ORDENAMIENTO_OK=1` y `ORDENAMIENTO_ERROR=0`; otros retornan void. Un rechazo conserva el estado aceptado; cuando hay traza del intento fallido, ésta explica la causa y no representa otra operación exitosa.

Ayuda: `/help/sorting`.

## Dudas rápidas

- **Siguiente está deshabilitado:** comprueba si llegaste al final o no preparaste traza. En un lote usa Siguiente valor al terminar el valor actual.
- **No cambia el dibujo:** una condición o retorno puede no cambiar datos; mira la línea C y Comprender.
- **No hay salida de consola:** muchas funciones no imprimen; revisa el resultado operativo.
- **Entrada múltiple inválida:** corrige la posición indicada, comas vacías, decimales, rango o duplicados antes de empezar.
- **La vista parece incompleta:** vuelve a 100%, desplázate dentro del dibujo y cierra memoria auxiliar.
- **Error del algoritmo:** lee la causa; un rechazo no añade una llamada exitosa. No confundas error de entrada con un error detectado durante la ejecución C.

## Teclado y memoria: referencia breve

Con una traza preparada y fuera de los campos:

- Secuenciales, Grafos, Hash y Ordenamiento: **Alt+→ / Alt+←**, siguiente/anterior; **Alt+Inicio / Alt+Fin**, comienzo/final; **Alt+P**, pausa.
- Secuenciales: **Alt+R** reproduce desde el inicio. Ordenamiento: reproduce o vuelve a empezar si llegó al final.
- Jerárquicas: **→ / ← / Inicio / Fin**, sin Alt; **Espacio**, pausa.
- Resultados: con foco en una pestaña, **← / →** cambia panel. **Tab** recorre controles.
- Durante un lote, usa sus botones propios.

Los identificadores de memoria del dibujo son **simbólicos**, no direcciones reales. Indeterminado no significa NULL. Después de `free`, los registros históricos explican el pasado, no permiten usar el puntero liberado. Copiar un puntero comparte el objeto: no crea un propietario independiente.

## Un primer programa C

### Referencia de rangos y propiedad

Los archivos C/H descargados no incluyen un programa principal; el programa que los usa conserva la responsabilidad de liberar sus reservas. En Rojo-Negro se aceptan enteros entre `-2147483648` y `2147483647`, sin truncar. Al terminar el programa usa `rbt_liberar(arbol); arbol = NULL;` para liberar los nodos propios y retirar el alias de la raíz.

Counting y Binsort usan `ORDENAMIENTO_RANGO_MAX=1000000` para el rango inclusivo máximo-mínimo+1. Binsort delega en Counting Sort y conserva sus límites y su retorno de éxito/error; el número de elementos no sustituye el cálculo del rango.

Descarga `tad_pila.c` y `tad_pila.h` desde Ayuda de Pila. Guarda al lado este `main.c`:

```c
#include <stdio.h>
#include "tad_pila.h"

int main(void) {
    ptrPila pila = NULL;
    pila_apilar(&pila, 10);
    pila_apilar(&pila, 20);
    pila_apilar(&pila, 30);
    if (pila != NULL) {
        printf("Sale: %d\n", pila_desapilar(&pila));
    }
    pila_destruir(&pila);
    return 0;
}
```

Con GCC: `gcc -std=c17 -Wall -Wextra main.c tad_pila.c -o ejemplo`.
Ejecuta `./ejemplo` (Windows: `.\ejemplo.exe`). Con reservas correctas imprime `Sale: 30`. Ese printf es del main, no de la función desapilar. El main del historial permite estudiar tus propias llamadas; revisa las firmas y reglas del encabezado de cada TAD.

### Leer líneas largas de código
El código actual, el main del historial y la estructura del TAD conservan sus líneas e indentación. Cuando una línea no cabe, usa la barra horizontal del propio panel; la barra vertical es independiente. También funciona en **Ampliar**. Al avanzar pasos no se centra el código horizontalmente: se conserva tu posición. Copiar C mantiene el texto original.
