# Conflicto preciso de25controles

Base aprobada:spec visual-playback-ui líneas10/28/179 exige modo manual,controles contextualizados ycincoetapas;permite otroscontroles pertinentes,no conteofijo ypreservar capacidades/contenido. Reconciliation-detailed REC1622–1626 (líneas2061–2065) sustituye disposición/etiquetas/visibilidad delalcanceanterior yordena conservarcapacidades. No autoriza por sísolo borrar funciones.

13IDs corresponden apresentación anterior:6botones jerárquicos(prepare,restart,home,end,pause,repeat)+hier-progress;5botonessecuenciales(prepare,start,end,pause,repeat)+seq-progress-slider. La implementaciónlosretira/oculta. Propósitosactuales ylíneasJS están endisposition25.json;Home/End/Space permiten navegar/pausar enjerárquicas;AltHome/End/P/R ymodomanual preservan propósitos ensecueconprueba nueva sinPOST. No declarar equivalenciaexacta deautoplay oarbitrarysliderseek donde sólohaylecturadesource. Esos IDs físicos siguenpendientes de mapeo/disposición formal;0exclusiones.

Conflicto documental secuencial:spec línea138 exige literalmente Ejecutar,Preparar yReproducir visibles;la regla posterior decontrolcompacto usaEjecutar/Pasoapaso/anterior/siguiente,ydisposición aprobada permitecambiarlabels/visibilidad sin perdercapacidades. Alternativa mínima:delta normativa que separe acciónnueva depreparar/navegar/reproducirtrazacache mediantecontrolesoatajosprobados,sin imponer esos3botonesexactos;mantener5etapas yprobar noPOST. Noaplicadoaquí;no elegir silenciosamente uncontrato contrapuesto.

12funciones pedagógicas quedaron sinflujo enjerárquicas:

- Predicción:hier-prediction,hier-hint,hier-skip-prediction,hier-practice-mode,hier-reset-progress (5).
- Comparación:hier-compare-kind,hier-compare-values,hier-compare-run,hier-compare-progress (4).
- Guiado/explicación:hier-learning-level,hier-guided-example,hier-load-example (3).

Fuente contrapuesta:static/js/hierarchical.js2331–2337 elimina seccionesPredecir/Comparar,selectoresnivel/ejemplo yload. Contrato líneas179–183 conserva contenidoadicional dentrodeetapas pertinentes;regla28 noelimina capacidad porel número debotones. Impacto: no practicar predicción/pistas/progreso,compararcopias ni cargar ejemplos/nivel desdeUI,aunquehooks/modelos históricos persisten. La existencia delmodelo/listener no demuestra flujoutilizable.

Alternativa mínima recomendada:no restaurarochoetapas ni widgets antiguos sinresolveralcance. Si esasfunciones permanecenencontrato,ubicarpredicción/comparacióncomodisclosures optativos enComprender (patrónsecueyaejecutado),guiadoenPreparar yniveldeexplicaciónenRelacionarconCódigo. Reutilizarhandlers ycasos aprobados verificandoC real/datospequeños;sin pasos repetidos/historiainventada. Si sepretendía retirarlas,registrardecisión explícita/deltas yrazónpedagógica antes decambiarinventario. Aquí no seimplementa restauración/exclusión ni seafirma autorizaciónindividual inexistente.

Internos entreestos25:0identificados;losespejos activos checkbox pertenecen aotrosIDs yse verificancomoestadointerno,pornocontrolpúblico. Clasificación sustentada no equivale aaceptación ni cierreC1.
