# Contrato de estado persistente de adapters

Cada adapter expone `export_state()` e `import_state(state)` para que la capa de
sesion pueda crear checkpoints sin conocer la representacion interna del TAD.
El estado visual (`to_visual_state`) no forma parte de este contrato.

## Reglas

- `adapter_version()` identifica la version compatible del payload. Su valor
  inicial es `"1"` y debe cambiar cuando una version anterior ya no pueda
  importarse sin migracion.
- `export_state()` devuelve un diccionario compuesto unicamente por valores
  compatibles con JSON: objetos, arreglos, cadenas, numeros, booleanos y `null`.
- El payload contiene solo estado necesario para continuar operaciones. No
  incluye HTML, cookies, objetos Python, funciones ni datos de sesion.
- `import_state()` valida el payload completo antes de modificar el adapter. La
  importacion es atomica: ante un error conserva el estado anterior.
- Un payload mal formado produce `AdapterStateError`; una version incompatible
  produce `AdapterStateVersionError`.
- Importar el resultado de una exportacion y volver a exportar debe producir el
  mismo estado semantico.

El sobre del checkpoint (estructura, posicion del historial, version, checksum)
pertenece al servicio de sesiones y se define por separado. Los adapters solo
son responsables de su payload interno.

## Activacion

Los checkpoints estan desactivados de forma predeterminada. Se configuran con:

- `ENABLE_CHECKPOINTS=false`: feature flag global.
- `CHECKPOINT_INTERVAL=50`: operaciones mutantes entre checkpoints.
- `CHECKPOINT_MAX_PER_STRUCTURE=1`: cantidad maxima conservada por estructura.

Las consultas no avanzan el intervalo ni crean checkpoints.
