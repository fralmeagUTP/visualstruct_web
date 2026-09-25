# Diseño: espacio jerárquico simple y sincronizado

## Flujo de la pantalla

Cada una de las cuatro estructuras jerárquicas conservará esta jerarquía:

```
1. Preparar y controlar la ejecución
   operación + datos + Ejecutar operación + Paso a paso
   [Anterior | Siguiente] sólo mientras el modo paso a paso esté activo

2. Visualizar y ejecutar       3. Relacionar con código C
   árbol, heap o arreglo           función C y resaltado de instrucción

4. Comprender (plegable)
5. Resultados de la ejecución (plegable)
   consola C + historial + TAD + exportaciones
```

La etapa 1 evita una fila extensa: no ofrece pausa, inicio, final, repetir ni velocidad como botones principales. **Ejecutar operación** crea una nueva ejecución o completa la traza en curso; **Paso a paso** abre el recorrido con Anterior y Siguiente. Los identificadores internos se pueden conservar para no romper el motor actual, pero la interacción visible debe respetar este contrato.

La etapa 3 se lee en vertical: el checkbox de documentación se alinea con su
título, el selector de funciones se presenta en una franja superior y el título
de la función junto con el bloque C ocupan todo el ancho debajo. No se usa una
columna lateral para el selector ni un desplazamiento horizontal global.

## Conservación del estado

La interfaz toma `visual_state` y `execution_trace` existentes como fuente de verdad. Cambiar de panel, plegar Comprender o Resultados y pasar entre las vistas responsive MUST NOT mutar la estructura, reiniciar la traza ni alterar el historial. Al alcanzar el último frame se presenta el snapshot canónico devuelto por backend.

## Presentación específica por estructura

| Pantalla | Estado visible | Lectura didáctica de la traza |
|---|---|---|
| ABB | raíz, hijos izquierdo/derecho, recorridos y orden de búsqueda | comparación, rama tomada, caso de eliminación y retorno recursivo |
| AVL | estructura de ABB, altura y factor de balance | desequilibrio, rotación LL/RR/LR/RL y árbol balanceado resultante |
| Rojo-Negro | nodos, enlaces, colores y raíz | inserción/eliminación, recoloreo o rotación, reglas de color y NIL cuando el modelo los represente |
| Montículo binario | arreglo indexado y árbol completo padre/hijos | inserción al final, comparación con padre y subida; sustitución de raíz y bajada al extraer |

El color no será el único medio para expresar una regla: etiquetas y Comprender describen decisión, comparación, invariante y variables del frame.

## Paneles secundarios

**Comprender** mantiene ruta, pila recursiva, variables, memoria, relaciones e invariantes ya producidos por la traza; inicia plegado para priorizar la operación. **Resultados de la ejecución** muestra como unidad consola C, historial, estructura estática del TAD y exportaciones. No habrá un `details` propio que permita ocultar sólo el TAD.

El selector de nivel, Ejemplo guiado, Predecir y Comparar se retiran de la interfaz de estas cuatro pantallas. Sus endpoints pueden permanecer internamente mientras no sean visibles ni requisito para avanzar una traza.

## Responsive y accesibilidad

- En escritorio, Visualizar y Código C se muestran lado a lado con ancho legible.
- La lista de funciones C se ajusta en varias filas dentro de su franja; los
  nombres extensos se parten de forma segura sin reducir el ancho del código.
- En móvil o ancho reducido, se conserva una alternativa de cambio de vista entre estado y código, accesible por teclado y con `aria-selected` correcto.
- Los botones tienen nombres claros, orden de foco lógico y tamaño suficiente.
- Los paneles plegables usan `aria-expanded` y no esconden contenido necesario para controlar la traza.

## Verificación manual planificada

Se abrirán ABB, AVL, Rojo-Negro y Montículo binario. En cada una se revisará carga, numeración, controles, visualización, código y paneles. Se ejecutará manualmente al menos una inserción y una operación característica (eliminación en árboles, extracción en heap) y se recorrerá una traza con Anterior/Siguiente. No se ejecutarán ni añadirán pruebas automatizadas.
