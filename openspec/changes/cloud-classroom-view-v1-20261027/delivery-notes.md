# Vista de clase v1 — revisión finita completada

## Qué cambia
- Imagen principal más grande junto al código C, con controles de zoom manual y desplazamiento local persistentes durante los pasos.
- Encabezados y preparación compactos, sin quitar identidad institucional ni campos de operación. Descripciones y opciones secundarias permanecen accesibles.
- Memoria auxiliar opcional fuera de la zona que se desplaza con el dibujo; el área principal se recupera al cerrarla.
- Resultados distribuidos en consola, `main.c` del historial y estructura del TAD; ampliación reversible y copia de texto real sin recargar ni ejecutar operaciones.
- Exportación preparada desde un clon independiente del zoom, desplazamiento y plegado de la memoria.

## Qué no cambia
C/H, algoritmos, backend Python, contratos, historial, significado de los pasos y libro no se modifican. Esta revisión no activa el coordinador de IA externa. La entrega v0, las instancias anteriores y los documentos originales se conservan.

## Evidencia verificada
El auditor visual ha usado el portapapeles real en cinco familias y ha compilado/ejecutado sus `main.c` contra el C descargado. La validación de la presentación es una matriz finita de casos, no una repetición completa de todas las operaciones semánticas de v0. La revisión técnica comprueba bytes de fuentes/backend, copia exacta, modos de consola y ausencia de mutación por ampliación/exportación.

La matriz visual independiente cierra 16 escenarios representativos a 1165×757 (viewport DOM 1180×757), con diez JPG de cinco familias más un JPG RN, cinco main copiados desde portapapeles real y compilados C17 estricto. El segundo viewport no se probó para no redimensionar la pantalla activa del usuario. La primera extracción fresca pasó a las 12:01:23 UTC: 5 archivos Node nuevos, 8 canónicos, 25 no-grafo y 2 scripts Python (9 main compilados/ejecutados y 5 plantillas). Forward reproduce el candidato; rollback restaura exactamente v0. La extracción del artefacto posterior al sello sigue siendo obligatoria y se registrará en verification.json antes de entregar.

## Reversibilidad
La entrega v1 es independiente de v0. Su overlay sólo podrá aplicarse sobre una copia cuyos hashes `before` coincidan. El rollback deberá restaurar exactamente v0; no borra ni despliega automáticamente sobre ninguna instalación. La aplicación completa extraída será el método más sencillo para probar sin modificar la versión anterior.
