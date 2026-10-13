# Propuesta MEDIUM acotada: stats Hash

Pendiente coordinación. Corregir tres regresiones de baseline sin cambiar H1/C_H ni añadir delta normativo.

Fuente real: caller THEstadisticas stats=th_estadisticas(&tabla),char texto[512],th_formatear_estadisticas; incluir cuerpos originales de ambos. Modelar tabla const, retorno THEstadisticas/copias propias caller/formatter, inicializador{0} con cinco campos (int,int,int,int,float), guardas, bucles i/nodos_en_bucket, actual y camposocupados/colisiones, conversionesfloat/operacionesC, máscaras semánticas/scopes. No leerpadding ni inventar ABI. El formateador invoca otra vez th_estadisticas: distinguir dos invocaciones y sus copias/lifetimes. snprintf fronteraopaca con truncamiento/terminación/guardas,textobuffer512 callerindeterminado.

Opciones numéricas explícitas:
A. Conservar API actual de tres campos/cociente Python y metadata6dec/mensaje3dec; traza C muestra float C y texto2dec de forma separada. Mantiene contrato existente sin falsa igualdad de representaciones. Recomendación para corrección instruccional acotada, requiere confirmación de coordinación de este alcance.
B. Alinear API/metadata a floatC: altera resultados observados y necesita decisión semántica explícita previa, no ejecutar silenciosamente. C convierte numerador/denominador a float antes de dividir; no basta redondear sólo resultado de división double para enteros grandes.

Conservar ocho IDs de baseline y134previos, cuatrofixtures/27buffers/ochoobservaciones como referencia sinsumar solapamientos. Journal/caller debe conservar dosconsultasstats,reproducir cálculoC yformateador conresultadoscomputados,C17/Doxygen/ownership, sin ampliar API a otros campos ni cerrar clear/destroy porcleanup. UIcinco secciones/helpers/scopes/buffer,recarga/replay sinredispatch,observerC independiente y recursos finitos antes decheckpointMEDIUM yLOW. No rendimientoarbitrario ni campaña global inventados.
