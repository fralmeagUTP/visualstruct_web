# Hash scopes/types: checkpoint MEDIUM para revisión LOW

Proyecto D:\MisProyectos\Web_VisualEstruct. Fecha UTC2026-10-03. Assignment coordination-hash-scope-fix-medium-20261003; operación hash.create-insert-scope-fix-medium. Instrucción nueva del coordinador01a0fe61-3104-743a-b032-bcc289ad80cd. Dos brechas corregidas y comprobadas; no cierre de métodos/global ni siguiente baseline.

## Cambios acotados

Solo app/domain/hash/creation_insert_instruction.py productivo: `pedagogy.variables` conserva locales/parámetros, y campos C se exportan como `tabla->capacidad`, `tabla->cantidad`, más struct_fields separado. init_entry conserva parámetrocapacidad3 y campo0 antes de la escritura. La memoria posee scopes explícitos por frame; tabla/claves del helper se representan como th_indice.tabla y th_indice.clave, con tipo const TablaHash* e int propios; alias misma raíz&tabla. Parámetros/indice helper desaparecen después de retornar, mientras indice del caller sigue indeterminado hasta la asignación. No cambiar C/H/kernel/adapter/callerJS/UIruntime ni semántica H1.

## Evidencia

95IDs originales pasan27.22s:93previos+2regresiones nuevas antesrojas, bytea byte intactos. Tres nuevos IDs parametrizados C17 pasan4.64s: capacidades3/17/1, claves-1/INT_MIN/INT_MAX; _Generic de int/const y alias de puntero real, comparados con estados/variables/scopes por instrucción API, colisión parámetrocapacidad vsfield incluido. Total98IDs distintos por collect;95+3 son conjuntos disjuntos, no se afirma una única suite98 ejecutada. Artefactos C17 de los tres tests preservados desde tmp sin sumar otro ensayo.

Se conservan comparaciones nativas previas34operaciones, máscaras/memoria/contadores/errores y cinco callers/Doxygen dentro de los95tests afectados. No sumar34+20UI ni repetir25faults ownership como cobertura nueva. Caller y C/H protegidos sin modificación.

Browser actual5051: cuatro casos/20operaciones,404framesadelante y384restauracionesatrás, con índice Cexacto, parámetros/campos distinguidos, tipo helperconst visible y expiración tras retorno,0POSTadicionales/0erroresJS,cinco secciones,recarga de traza idéntica. Preview propio10024/16576 ejecuta D/run.py en127.0.0.1:5051.

protected-before/after iguales:95tests existentes, tres regresiones iniciales, HashC/H, onceSorting y arnés compartido. Guardas before/after. Se agrega tests/test_hash_scope_fix_native.py y arnés UI propio; fuentes anteriores y fallos rojos conservados.

## Límites y revisión LOW

Pruebas nativas de tipos/alias para parámetros más observador de escalares/memoria previo; no certificación de todos los tipos/variables/arbitrarios C ni direcciones físicas persistentes. Otros nueve métodosHash pendientes. Recursos medidos antes de este cambio son históricos: nueva información scope agrega snapshots/JSON; revisar overhead finito enLOW antes del cierre, no dominio gigante, OOMreal,RSS/SLA universal. UIcasos4son verificación repetida fundada por el cambio de representación, no nuevas20operaciones de cobertura. LOW debe consolidar estas brechas ya verdes y límites antes de declarar cierre finito. No siguiente baseline, RN/Grafos, publicación, commit/push/merge/despliegue. Global13/22/docs121/208/11Sorting sinincremento.
