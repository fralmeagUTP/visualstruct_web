# Propuesta revisable: Validar Rojo-Negro completo

Estado: **pendiente de decisión del usuario; no implementada**. Hallazgo
`C-RBT-VALIDAR-LIMIT-01` permanece OPEN, severidad media. El cierre registrado de
los siete métodos para casos auditados no resuelve esta limitación.

## Problema demostrado y comportamiento propuesto

El backend actual (`tad_wrappers.py`, `RojoNegro.validar/_validar_rec`) y los
auxiliares C canónicos del main (`CCodeService._build_red_black_data`) comprueban
raíz negra, orden estricto y ausencia de rojo-rojo. No comprueban altura negra ni
`padre`. El auxiliar `rbt_validar` actual pertenece a la aplicación/main: no está
exportado por el C/H descargable.

Dos contraejemplos reproducibles con reservas vivas:

| Grafo preparado | Resultado actual | Resultado deseado, aún no ejecutado |
|---|---|---|
| Raíz10 negra, hijo5 negro, otro hijoNULL | True/1 aunque las alturas negras difieren | False/0 |
| Raíz10 negra, hijo5 rojo, `hijo.padre=NULL` | True/1 aunque el enlace al padre es incorrecto | False/0 |

La observación LOW compara backend, auxiliar C real del main y un comprobador
nativo independiente; no modifica el validador. Evidencia en
`evidence/red-black-validator-extension-proposal-low/`. No es una ejecución de la
solución propuesta.

## Alternativas e impacto

| Opción | Resultado y cambios | Consecuencia |
|---|---|---|
| V1: conservar validador parcial | Mantener las tres comprobaciones y la advertencia explícita en guía/resultado | No cambiar semántica; aceptar expresamente que OK no certifica Rojo-Negro completo. El hallazgo se registra como limitación aceptada, no como corrección implementada |
| V2: ampliar auxiliares de aplicación/main | Añadir altura negra, padres y color válido al backend y al C mostrado/generado, conservando bool/1/0 | Menor cambio público, pero el C/H descargable continúa sin ofrecer Validar; el estudiante necesita el main generado y sus auxiliares |
| **V3 recomendada: contrato completo también en C/H** | Exportar `int rbt_validar(RBT raiz)` y un helper privado de comprobación en el TAD real; replicar el contrato en backend y observar esas funciones exactas | C/H, código mostrado, main y guía comparten una fuente clara. API C aditiva; mismo método visible y mismo resultado bool/1/0. Requiere actualizar trazas y evitar definición duplicada en el main |

Recomendación V3 por la prioridad explícita del usuario sobre los archivos que
descargan los estudiantes. No cambia algoritmos de Insertar/Eliminar, no agrega
botones o métodos al menú y no repara automáticamente un árbol inválido.

## Contrato exacto propuesto para V2/V3

- Entrada: raíz prestada, NULL admitido. Los nodos y los campos puntero que se
  examinen deben referir objetos vivos válidos o NULL. No promete diagnosticar
  punteros arbitrarios o memoria liberada mediante desreferencia.
- Resultado: 1/True para vacío o representación válida; 0/False si falla alguna
  propiedad. Una consulta válida con resultado False conserva éxito de ejecución
  de la operación; no se convierte en error HTTP ni en mutación.
- Comprobar raíz negra; cada color pertenece a ROJO/NEGRO; orden estricto sin
  duplicados; ausencia de rojo-rojo; raíz con padreNULL y cada hijo con padre
  exactamente igual al nodo propietario; altura negra uniforme.
- Los padres se comparan por identidad (`is` en Python, comparación de punteros
  vivos en C), no por igualdad estructural de nodos o de la vista NIL.
- Los límites BST usan indicadores `tieneMin/tieneMax`, sin centinelas numéricos,
  `nro-1` o `nro+1`, para admitir INT_MIN/INT_MAX sin overflow.
- Convención interna: altura negra de NULL=1, igual al oráculo existente. Es una
  hoja conceptual, no una reserva NIL. El resultado público continúa siendo
  bool/1/0; no se añade un resultado numérico nuevo a la API.
- Solo lectura: no reserva/libera, cambia enlaces/colores, imprime ni reejecuta
  historial. Cada ámbito y llamada se representa por instrucción; una condición
  falsa omite el trabajo siguiente cuando el C usa cortocircuito.

Esquema **documental**, no código implementado:

```text
comprobar(n, padreEsperado, límites):
    si n es NULL: retornar 1
    si n.padre != padreEsperado: retornar inválido
    si color no es ROJO/NEGRO u orden exclusivo falla: retornar inválido
    si n es rojo y un hijo vivo es rojo: retornar inválido
    izquierda = comprobar(n.izq, n, límites restringidos)
    si izquierda es inválida: retornar inválido
    derecha = comprobar(n.der, n, límites restringidos)
    si derecha es inválida o izquierda != derecha: retornar inválido
    retornar izquierda + (n es negro ? 1 : 0)
```

La combinación de padre esperado, raíz con padreNULL y límites estrictos permite
rechazar ciclos/enlaces compartidos lógicos antes de repetir indefinidamente una
cadena de objetos vivos. Esta propiedad debe demostrarse con fixtures; no se
declara verificada por este pseudocódigo. Para clasificar explícitamente
«ciclo» frente a «padre/orden incorrecto» puede usarse un registro de visitados
(O(n) memoria), pero añade política de fallo de memoria/diagnóstico y no se
incluye silenciosamente. El retorno booleano no necesita esa clasificación.

Complejidad pretendida: O(n) tiempo/O(h) pila en árboles válidos; salir al primer
fallo. No certificar complejidad o terminación de grafos inválidos sin pruebas.

## Cambios concretos si se aprueba V3

1. Añadir el contrato Doxygen, función pública y helper privado a
   `docs/tads_C/tad_rojo_negro.c/.h`. Actualizar inventario/denominador documental
   desde símbolos reales; no sumar revisiones ficticias ni suponer un conteo.
2. Actualizar `RojoNegro.validar/_validar_rec` conservando resultado/esquema de
   operación e historial. Validar propiedades del modelo nativo, no de la vista
   NIL reconstruida, que puede ocultar un `padre` original incorrecto.
3. Cambiar CCodeService para obtener Validar de la fuente real y mostrar sus
   helpers. Adaptar el modelo de instrucciones, argumentos, retornos internos,
   cotas, char/altura negra, condiciones y ámbitos en ambas vistas/replay.
4. El main deberá **llamar la función exportada** al enlazar el TAD, sin volver a
   definir `rbt_validar` dentro del main. Conservar consultas exitosas repetidas,
   separación entre resultado de la aplicación y printf real del caller y
   limpieza final del propietario fuera del historial.
5. Actualizar ayuda/manual y referencias al contrato parcial. C/H HTTP y main
   deben compilar juntos C17/Werror y pasar Doxygen con exactitud por contenido.
6. Crear delta OpenSpec y asignación específica aprobada para la extensión antes
   de implementarla. Conservar evidencias históricas del validador parcial como
   contrato supersedido; ajustar sus expectativas únicamente por el requisito
   nuevo, manteniendo pruebas negativas.

## Verificación requerida después de aprobar

- Vacío, hoja, árboles válidos obtenidos por inserciones/eliminaciones,
  INT_MIN/INT_MAX y casos con varias alturas negras iguales.
- Raíz roja, rojo-rojo, duplicado, infracción de cota ancestral y color inválido.
- Los dos contraejemplos anteriores; raíz con padre noNULL, hijo con padre
  incorrecto, ciclos directos/interiores y nodo compartido. Fixtures contienen
  solo objetos vivos; liberarlos por registro de reservas únicas, nunca con un
  recorrido destructor cíclico.
- Comparación independiente C/backend/resultados y observación por instrucción:
  ámbitos, altura retornada, padre esperado, selección/cortocircuito, resaltado,
  consola, heap sin mutación y ambas vistas adelante/atrás sin POST adicional.
- Casos cíclicos no se expondrán como operación nueva. Validar C/backend en
  fixtures controlados; no serializar recursivamente un grafo inválido mediante
  una vista que asuma árbol. Si se necesita UI test-only, usar proyección segura
  de reservas/identidades y explicar el transporte artificial.
- Descargas HTTP y main real antes/después de reload; estado/historial idénticos,
  cero alloc/free del validador, compilación estricta y revisión Doxygen/manual.
- Regresión focal Insertar/Eliminar/Limpiar y consultas. Después, revisión final
  agregada coherente del aplicativo; sanitizador/WebKit siguen como límites si
  no están disponibles.

## Decisión solicitada

Elegir V1, V2 o V3. Si se aprueba V3, confirmar que se agregue la función a C/H y
se mantenga el resultado booleano público, con detección de grafos lógicos
inválidos sobre referencias vivas. Diagnóstico estructurado adicional y examen
de punteros inválidos quedan fuera de esa autorización. Hasta responder:
**ninguna extensión implementada y hallazgo OPEN**.
