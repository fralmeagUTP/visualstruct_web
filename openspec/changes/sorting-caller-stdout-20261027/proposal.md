# Salida real del caller de Ordenamiento

## Por qué

El programa C descargable puede imprimir desde main aunque el cuerpo del algoritmo no tenga printf. Si la traza solo describe el TAD, la consola omite salida real del programa o puede mostrarla con una atribución incorrecta.

## Qué

Conciliar la ejecución/traza de Ordenamiento con las instrucciones de impresión reales del caller generado, manteniendo separada su procedencia respecto del algoritmo. Preservar los C/H exactos, los estados didácticos y la navegación del historial. Verificar el contrato con compilación y ejecución C17 del programa real, además de pruebas finitas del backend.

No cambia el layout, los archivos canónicos ni otros módulos; no incorpora síntesis de stdout desde el arreglo final.
