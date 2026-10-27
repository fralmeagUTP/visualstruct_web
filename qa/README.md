# Regresiones de reparación pedagógica — 2026-10-27

Esta carpeta contiene pruebas nuevas y finitas de la copia de reparación. **No es la suite histórica de 530 pruebas mencionada anteriormente por el proyecto.** Los datos JSON son fixtures de trazas/estado; algunos scripts de generación se ejecutan por separado. Un método unittest, un escenario, un frame y una operación UI no son unidades equivalentes.

## Ejecución local
Las pruebas diferenciales necesitan además los baselines y fixtures independientes vecinos a la aplicación. Para reproducir el paquete, extrae `visualstruct-repaired-app.zip` y `visualstruct-independent-evidence.zip` **en el mismo directorio padre**: `visualstruct_web-main/`, `qa_trazas/`, `qa_frontend_main/`, `scope-insert-baseline/` y los cuatro archivos `*-baseline.py` deben ser hermanos. No basta con extraer únicamente el ZIP de la aplicación.

Desde `visualstruct_web-main/`, con sus dependencias Python ya disponibles y Node:

```sh
python -m unittest discover -s qa -p 'test_*.py' -v
for test in qa/test_*.js; do node "$test" || exit; done
```

No requiere navegador, credenciales, red ni despliegue. Las pruebas HTTP usan clientes Flask y almacenamiento temporal. Algunas pruebas invocan GCC local. Las compilaciones C estrictas/ejecuciones y el recorrido real de navegador tienen evidencia independiente complementaria, no se sustituyen por este comando.

## Contratos cubiertos
- Frontera API/C: enteros representables, posiciones, valores opcionales, historial preservado y rechazo antes de ejecutar C.
- Reproductor: avance/pausa/carga/retroceso; resaltado y estado coherentes; respuesta tardía no repinta una traza cancelada.
- Código legible: comentarios no ocultan escrituras por punteros; ajuste de línea y desplazamiento local; copiar C no añade NBSP.
- Comprender: resumen contextual, metadatos fuera de la narración principal, variables C legítimas preservadas.
- Memoria: reservas, aliases, inicialización y liberación simbólicas; ámbitos terminados no aparecen activos.
- Consola: mensajes de aplicación separados de stdout; snapshots/eventos/raw explícitos, con repeticiones y espacios legítimos.
- Consulta/resultado: publicación sólo al final pertinente y reversión al retroceder.
- Hash: máximo educativo128, historial superior suspendido antes de reconstrucción, sin borrar historia/main; rechazo sin escrituras; reset explícito. No se modifica el límite del TAD C. Capacidades extremas se prueban con reconstrucción prohibida por mocks, no se reservan realmente.
- Exportación: descarga y expansión de clon sin alterar el DOM visible; evidencia de píxeles descargados se conserva aparte.

## Límites
Los tests DOM ligeros no prueban por sí solos píxeles, accesibilidad completa ni todos los tamaños de pantalla. El recorrido UI independiente se realizó en el viewport indicado en su matriz y en casos definidos. Controles realmente ocultos se marcan NOT_EXPOSED, no como aprobados por navegador. La comparación integral libro/grafo permanece pendiente de decisión canónica; el único cambio del TAD C es el guard mínimo de invariantes de reserva del cambio OpenSpec separado. El coordinador IA se entrega por separado y no se ha verificado operativo con un ejecutor IA real.
