# Siguiente metodo propuesto: Seleccion por instruccion

Preparacion solamente; no implementado ni ejecutado. Requiere nueva asignacion fina sorting.seleccion-instructions y guarda before, no escoger este bloque desde un checkpoint historico. Intercambio permanece cerrado; su observador/frames y caller consolidado son infraestructura de referencia, no autorizacion de repetir casos.

## Infraestructura reusable

tests/_audit_intercambio_instructions.py conserva descargaC/H, extraccion de cuerpos reales, observacion independiente C17, snapshots before/after y comparacion API. Separar en una utilidad comun de extraccion/compilacion/observacion cuando Seleccion se asigne; no crear un sorter nativo en Python ni inferir eventos del resultado final. Reusar tests/_audit_sorting_main_native.py para verificar caller realmente descargado, Doxygen y ownership. Reusar la navegacion real, el modo tecnico y capturas de browser de Intercambio, sin modificar su motor ni afirmar cobertura de otros metodos.

## Contrato a observar

ordenar_seleccion(int arreglo[],size_t n) es void. Declaraciones size_t i/j/indice_menor, valida arreglo con cortocircuito, for exterior/interno y sus pruebas falsas/incrementos, indice_menor=i, cada comparacion arreglo[j]<arreglo[indice_menor], actualizacion del minimo solo cuando es menor, guarda indice_menor!=i tras terminar el ciclo interno y llamada a intercambiar(&arreglo[i],&arreglo[indice_menor]) solo cuando es verdadera. Si indice_menor==i, la guarda es falsa y NO se llama al helper; no fabricar asignaciones ni autoalias. No confundir menor provisional con posicion confirmada. i/j pueden alcanzar sus limites antes de una prueba falsa, no se fabrican accesos fuera de rango. Mantener locals sin inicializar, scopes, temporal/punteros, ciclo caller suspendido y retornos.

## Casos acotados propuestos

Seis entradas maximo4: [7], [1,2], [2,1], [2,2], [-3,0,-1,0], [INT_MAX,INT_MIN,0]. Ascendentes/duplicados observan la guarda de swap falsa y ausencia de helper; inversos/negativos observan cambio de minimo y swap real. NULL/n0 nativos separados del rechazo API/UI vacio. Duplicados int no verifican estabilidad de identidades. Contrastar cada evento/linea/condicion/indices/alias/temp/movimientos/estado con C descargado, avanzar/retroceder en arreglo y estrategia reales sin POST. Main de los casos descarga por /help/source/sorting_array/main y debe contener los runs reales, no crear otro renderer.

## Cierre posterior

Solo estas entradas y guardas; nunca once metodos por una suite endpoint. Mantener Grafos numericos pendientes, cinco secciones,5051 y global13/22. Sin push/merge/despliegue. Consultar coordinacion si la semantica necesita MEDIUM acotado; regresar LOW al concluir. No usar este plan como instruccion de implementacion actual.
