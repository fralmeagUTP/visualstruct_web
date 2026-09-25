# Diseño: piloto de laboratorio compacto para Pila

## Disposición de escritorio

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Preparar: operación, dato, nivel y ejemplo                       │
├──────────────────────┬──────────────────────┬───────────────────────┤
│ 2. Ejecutar y        │ 3. Relacionar con C  │ 4. Controlar la       │
│    visualizar        │ función, línea y     │ ejecución: ejecutar,  │
│ pila, TOP y memoria  │ desplazamiento interno│ reproducir y pasos    │
└──────────────────────┴──────────────────────┴───────────────────────┘
  5. Predecir · 6. Comprender · 7. Comparar · 8. Reflexionar: bajo demanda
```

## Jerarquía de información

1. **Siempre visible:** operación, entrada, Ejecutar, Reproducir, Siguiente,
   estado visual, código C activo y estado breve de la simulación.
2. **Visible al necesitarlo:** velocidad, navegación extensa, predicciones y
   tablas de variables/punteros.
3. **Bajo demanda:** comparación, historial técnico, consola completa,
   estructura C y exportaciones.

## Secuencia y paneles

La interfaz conserva una numeración única y ordenada: **1 Preparar**, **2
Ejecutar y visualizar**, **3 Relacionar con C**, **4 Controlar la ejecución**,
**5 Predecir**, **6 Comprender**, **7 Comparar** y **8 Reflexionar**. Las
etapas 5, 6 y 7 se muestran como paneles plegables, cerrados inicialmente para
dar prioridad al trabajo inmediato. Cada resumen indica su propósito y conserva
la apertura elegida durante la sesión.

## Comportamiento adaptable

- Escritorio: tres áreas, con altura de trabajo basada en la ventana; los paneles
  de código y auxiliares desplazan internamente.
- Tableta: controles arriba, estado y código en dos paneles reducidos o pestañas.
- Móvil: controles pegajosos, pestañas Estado/Código y paneles progresivos.

## Restricciones de fidelidad

El rediseño no transforma ni interpreta la traza: estado visual, código
resaltado, consola y controles siguen consumiendo los mismos frames canónicos.
