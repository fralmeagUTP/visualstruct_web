# Mensaje de Lista y40controles: balance finito

Mensaje corregido:insertar_elemento exitoso enposition1 indica al inicio, conforme al Ccanónico;position>1 conserva antes/después. Tresregresiones API PASS verifican texto ylista resultante (pos1/relative0,pos1/relative-1,pos2/relative0). Sólo se añadió la rama descriptiva deladapter;sin modificar algoritmos niC. Primera colección detectó error deindentación delaedición ylecturaBOM;amboscorregidos antes de ejecutar casos,registrosconservados. Findingsnapshot original sigueintacto;resolución nueva text40-finding-resolution.json. DeltaOpenSpec propia añadida.

Los40IDs asignados fueron revisados.15vínculos de comportamiento ejecutado,mediante11casos E2E distintos:13widgets públicos y2espejos internos.25IDs conservan requisitos pendientes porfalta deflujo enUIvigente. Registro238vinculados/137pendientes→253vinculados/122pendientes;0aceptaciones globales,0requisitos eliminados. Gate15asignaciones sinerrores. DiagnósticoDOM sólo descubrecontextos,no secontó comocobertura.

| Flujo | CasosE2E PASS | IDs vinculados |
|---|---:|---:|
| Cambiar modo manual conbotón público |4|5(incluye2espejos ocultos) |
| Ocultar/restaurar comentarios C reales |3|3 |
| Reset degrafo propio ydownloadmainC Pila |2|2 |
| Comparación conceptual opcional ypredicción/progreso |2|5 |
| Total |11|15 |

Se verificaron checkbox/aria-pressed activados ydesactivados,comentarios visibles que seocultan yvuelven,reset conconfirmación deja grafo vacío,downloadmain.c conapilar7 yliberación,slider LIFO/FIFO→selecciónporprioridad,cambio detipo reiniciacursor sinPOST,práctica oculta/revela visualización yunarespuesta seguida dereset deja progreso0/0. Los controles opcionales requirieron abrir Comprender→Comparar/Predecir mediante susdisclosures públicos. Comparación esdemostraciónconceptual delUI,no ejecuciónC nativa ni prueba depolíticasdetodosTAD.

Los2camposinternos(graph-step-toggle,hier-step-toggle) secomprobaron mediante botones públicos;NOse actuaron ni enfocaron directamente yNOse calificaron como widgets interactivos. Losvínculos registran estealcance ysiguen sinadmisión. Pruebas decomentarios iniciales Graph/Hash no tenían estímulo/clase adecuadas;se seleccionóPrim/keys reales yclasescomentario correctas,con fallos previosretenidos. Caso jerárquico reverificado alactualizar selector;no sumarretests como casosadicionales.

25brechas reales deflujoactual (no ausenciaabsoluta depruebas):19jerárquicos sonretirados porlaadaptación decincosecciones enstatic/js/hierarchical.js;5botonessecuencialeslegacy sonocultados y1slider técnicoretirado enstatic/js/sequential.js. Líneas/hash/IDs yacción enclassification40.json/blocked25.csv. Requierenmapeo acontrolesvigentes odecisión explícita deinventario/spec;no forceclick,unhide,reanimación deflujosretirados niexclusiónsilenciosa.

Bloques privados120s/2GiB:modo14,875s/252,4MiB;comentarios seleccionados9,766s/245,15MiB+jerárquico4,781s/232,88MiB;reset/download8,641s/244,72MiB;opcionales9,282s/247,96MiB;regresióntexto1,281s/40,86MiB. Ningún límite alcanzado. Sesiones/cookies/browser propios;runtime/templateloader Dcanónico comprobados.26fuentesC byteidénticas contra fotografíaDprevia y3904sesiones byteidénticas. SinDocker,preview5051,commit/push/despliegue ni campañas consumidas.

Pruebas permanentes:tests/test_controls40_real_flows.py,tests/test_list_insertion_instruction_text.py. Fuente,ejecución yaceptación porseparado;no cierre globalC1 ni certificaciónC porinstrucción. Siguienteacción fuera deestebloque:mapeo/decisión de25IDs disponibles ensuCSV,conasignaciónnueva.
