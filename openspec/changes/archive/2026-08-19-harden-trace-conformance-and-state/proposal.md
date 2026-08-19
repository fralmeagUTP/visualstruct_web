# Propuesta: endurecer trazas, conformidad C y reconstrucción de estado

## Why

VisualEstruct tiene una base didáctica sólida, pero concentra responsabilidades críticas en
`ExecutionTraceService`, reconstruye cada estructura reproduciendo todo su historial y asume
la equivalencia entre las implementaciones Python y C sin validarla automáticamente.

Los hallazgos que motivan esta propuesta son:

- `ExecutionTraceService` supera las 4.300 líneas y mezcla interpretación, reglas por TAD,
  generación de estados, mensajes y control de flujo.
- El replay completo puede ejecutar hasta 300 operaciones en cada solicitud.
- Los 13 TAD C compilan con C17, pero no existe un harness que pruebe memoria, comportamiento
  indefinido ni paridad observable con Python.
- La cobertura global es 83%, pero varios motores de dominio críticos están por debajo de 60%.
- La configuración permite conservar en producción la clave de desarrollo y confiar en
  `X-Forwarded-*` por defecto.
- Las pruebas E2E dependen de una instalación manual de Chromium en entornos locales.

## What Changes

1. Se introduce un contrato estable `TraceStep` y un motor de trazas compuesto por estrategias
   independientes para secuenciales, árboles, grafos, hash y ordenamiento.
2. Se añade un runner de conformidad que ejecuta escenarios equivalentes contra Python y C y
   compara resultados, errores y estado observable normalizado.
3. El estado de sesión incorpora checkpoints versionados para evitar el replay completo sin
   perder determinismo ni compatibilidad con historiales existentes.
4. La CI compila y prueba los TAD C con advertencias estrictas, sanitizers y pruebas
   diferenciales; además aplica umbrales de cobertura por componentes críticos.
5. La aplicación valida la configuración sensible al arrancar en modo producción.
6. La suite E2E se identifica explícitamente y ofrece un comando reproducible de instalación y
   ejecución local.

## Fuera de alcance

- Reescribir la aplicación o sustituir Flask/JavaScript vanilla.
- Ejecutar código C proporcionado por usuarios dentro del servidor web.
- Cambiar las operaciones, nombres o resultados públicos de los TAD existentes.
- Añadir nuevas estructuras de datos.
- Rediseñar visualmente toda la interfaz.

## Impacto esperado

- Menor riesgo de regresión al modificar una familia de estructuras.
- Evidencia automática de fidelidad entre el material C y el simulador Python.
- Latencia de reconstrucción acotada para historiales largos.
- Fallos de configuración inseguros detectados antes de servir tráfico.
- Pipeline de calidad reproducible tanto en CI como en desarrollo.

## Riesgos y mitigaciones

- **Cambio de trazas existentes:** congelar primero casos golden y migrar una familia a la vez.
- **Diferencias legítimas C/Python:** comparar un estado observable canónico, no detalles de
  representación interna.
- **Checkpoints obsoletos:** versionarlos y hacer fallback seguro a replay completo.
- **Sanitizers no disponibles en Windows:** ejecutar el gate principal en Linux CI y conservar
  compilación C17 portable en Windows.

## Criterio de finalización

La propuesta estará completa cuando todas sus tareas estén verificadas, la suite existente no
regrese, cada familia use el nuevo contrato de trazas, los 13 TAD participen en conformidad y el
replay con checkpoints cumpla el presupuesto de rendimiento definido en los deltas.
