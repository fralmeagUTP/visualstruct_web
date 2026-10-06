"""Didactic help content for hierarchical structures."""

from __future__ import annotations

from typing import Any
from copy import deepcopy


class HierarchicalHelpService:
    """Serve educational texts for the hierarchical module."""

    _MODULE_HELP = {
        "title": "Ayuda del modulo jerarquico",
        "description": (
            "Este modulo permite estudiar arboles como interprete visual de codigo C: "
            "la simulacion muestra comparaciones, inserciones/eliminaciones y ajustes "
            "de balance en el mismo orden en que se ejecutan las subrutinas."
        ),
        "tips": [
            "Usa Ejecutar operación en modo rápido para el resultado; activa Paso a paso antes de otra ejecución para revisar Siguiente paso y Paso anterior.",
            "En ABB/AVL revisa la ruta de comparaciones; en AVL/Rojo-Negro verifica el momento exacto del rebalanceo.",
            "Despues de cada mutacion confirma validacion, recorridos y coherencia del arbol final.",
        ],
    }

    _STRUCTURE_HELP: dict[str, dict[str, Any]] = {
        "abb": {
            "title": "ABB",
            "summary": (
                "Arbol binario de busqueda sin duplicados: todo valor menor va al subarbol izquierdo "
                "y todo valor mayor al derecho. En la simulacion revisa la ruta de comparaciones y "
                "confirma que la propiedad de orden se preserve despues de cada insercion o eliminacion. "
                "Buscar retorna un puntero prestado o NULL en C; la interfaz expone encontrado o "
                "no encontrado como booleano, sin error por ausencia. El llamador equivalente "
                "mostrado contextualiza esa conversion y no agrega otro metodo al C/H descargado. "
                "Minimo y maximo recorren enlaces con while, sin recursion ni mutacion; retornan "
                "un alias prestado. En C, arbol vacio retorna NULL; el wrapper consulta el TAD y "
                "convierte ese retorno en un error de interfaz. "
                "En ABB, altura cuenta niveles: vacio 0 y hoja 1. altIzq y altDer son locales int de "
                "cada invocacion; durante su inicializador recursivo estan en ambito, sin inicializar. "
                "El padre conserva sus locales mientras espera al hijo. La altura visita todo el arbol "
                "en O(n), con O(h) marcos recursivos, sin cambiar enlaces ni imprimir. "
                "La interfaz rechaza duplicados y "
                "eliminaciones ausentes; el TAD C conserva el arbol en esos casos. Asigna a la raiz "
                "el retorno de insertar/eliminar. liberarArbol recibe la raiz por valor: despues "
                "de liberar, el llamador debe ponerla a NULL. Durante Limpiar, free termina primero "
                "las vidas de hijos y despues del padre; sus alias se muestran como identidades "
                "historicas con valor indeterminado, nunca como direcciones utilizables. El SVG "
                "representa reservas vivas y no afirma que el C haya puesto sus enlaces a NULL. "
                "El retorno es void y la asignacion NULL del main es una instruccion posterior. "
                "Durante Eliminar, la llamada recursiva no publica enlaces futuros: el retorno "
                "se asigna despues. Con dos hijos se conserva la reserva encontrada y se copia "
                "el valor del sucesor; ambas reservas existen temporalmente con ese valor. "
                "El helper minimo tiene su propio ambito; temp se inicializa al retornar. "
                "free termina solo la reserva retirada; sus alias son historicos inutilizables. "
                "Los recorridos C imprimen cada entero "
                "seguido de un espacio, sin salto final. Contar hojas y Validar usan auxiliares "
                "mostrados en la aplicacion que no estan declarados en el C/H descargado. "
                "Contar hojas retorna 0 para NULL y 1 para un nodo sin hijos; en otro caso suma "
                "los conteos de ambos subarboles sin mutacion ni printf. C no fija cual llamada "
                "de esa suma se evalua primero: un orden mostrado u observado es una opcion "
                "permitida, no una garantia del lenguaje. Los resultados parciales son operandos "
                "de la expresion, no variables locales declaradas. El main mostrado con Contar hojas "
                "incluye stdio.h, tad_abb.h y el auxiliar canonico una sola vez; compilalo junto a "
                "tad_abb.c. Imprime el conteo calculado, conserva consultas repetidas y las recupera "
                "al recargar sin volver a ejecutarlas para reconstruir el arbol. "
                "Validar ABB usa limites estrictos opcionales con indicadores enteros: la llamada "
                "inicial omite ambos limites y admite INT_MIN/INT_MAX. No usa sentinelas ni +/-1. "
                "Cada hijo hereda los limites de sus ancestros; igualdad o duplicado devuelve 0. "
                "NULL devuelve 1. El cortocircuito omite limites ausentes y no visita el subarbol "
                "derecho si el izquierdo falla. Es consulta sin mutacion ni printf; cada marco "
                "conserva sus parametros. El main incluye el auxiliar una sola vez y calcula "
                "cada validacion, sin imprimir una respuesta almacenada de la interfaz. "
                "Consultas repetidas sobreviven a recarga sin volver a ejecutar esas operaciones del historial al reconstruir."
            ),
            "supported_operations": [
                "insertar",
                "eliminar",
                "buscar",
                "minimo",
                "maximo",
                "altura",
                "contar_hojas",
                "inorden",
                "preorden",
                "postorden",
                "validar",
                "limpiar",
            ],
            "pending_operations": [],
        },
        "avl": {
            "title": "AVL",
            "summary": (
                "Arbol AVL auto-balanceado: mantiene factor de equilibrio por nodo en el rango [-1, 1]. "
                "La animacion debe mostrar deteccion del nodo desbalanceado y aplicacion de rotaciones "
                "(LL, RR, LR, RL) sincronizadas con la linea C que se interpreta."
                " Las rotaciones C conservan valores y reservas, reenlazan padres/raiz y "
                "actualizan FE como altura(derecho)-altura(izquierdo), sin poner ambos a cero. "
                "Las simples calculan primero A y luego B con formulas O(1); las dobles componen "
                "dos simples sin preasignar FE. Tambien contemplan hijo equilibrado al eliminar "
                "y nieto FE-1/0/1. El llamador mantiene factores de ancestros; durante la "
                "reconexion y antes de actualizar FE no se debe afirmar un AVL terminado. "
                "Estas correcciones nativas no certifican por si solas cada traza visual. "
                "Eliminar retorna void y no imprime. Con dos hijos intercambia el valor con el "
                "sucesor y libera su reserva; la reserva encontrada inicialmente puede seguir viva "
                "con otro valor. Sin hijos o con uno, publica el enlace y el padre del hijo antes "
                "de free. Los alias de la reserva retirada dejan de ser utilizables. Vacio/ausencia "
                "son rechazos web; el C deja el arbol intacto. El reequilibrio recalcula alturas "
                "y puede visitar la nueva raiz del subarbol despues de rotar. "
                "Validar muestra un auxiliar de equilibrio por alturas: no revisa orden ABB ni FE almacenado. "
                "El backend revisa orden y equilibrio por separado. NULL retorna 1 en el auxiliar; "
                "la primera diferencia fuera de -1..1 corta la recursion. Su traza elige altura "
                "derecha y despues izquierda, aunque C permite otro orden de operandos de la resta. "
                "El main del historial reproduce consultas exitosas, incluidas repeticiones; "
                "recargar conserva esas consultas sin ejecutarlas otra vez. Maximo, Inorden y "
                "equilibrio por alturas usan los auxiliares mostrados, incluidos una vez en ese "
                "programa; no son exportaciones del C/H descargable. Inorden imprime valores "
                "ascendentes, no avl_verArbol. La comprobacion de equilibrio por alturas no "
                "certifica el FE almacenado. Compile el main junto a tad_avl.c; los rechazos "
                "se anotan sin ejecutar la llamada fallida."
            ),
            "supported_operations": [
                "insertar",
                "eliminar",
                "buscar",
                "minimo",
                "maximo",
                "altura",
                "inorden",
                "validar",
                "limpiar",
            ],
            "pending_operations": [
                "El TAD no expone informacion textual de rotaciones realizadas.",
            ],
        },
        "red_black": {
            "title": "Rojo-Negro",
            "summary": (
                "Arbol balanceado por reglas de color (rojo/negro) que limitan la altura. "
                "Durante la simulacion observa recoloreos y rotaciones para mantener raiz negra, "
                "sin rojos consecutivos y con altura negra consistente entre caminos. "
                "La consulta Validar publica del TAD comprueba las cinco reglas RN y orden estricto; "
                "comprueba altura negra uniforme, colores y enlaces al padre sobre objetos vivos. Inorden y Altura "
                "usan auxiliares documentados de la aplicacion/main, no exportados por el C/H. "
                "Inorden imprime valores ascendentes con espacio final, sin salto; Altura "
                "cuenta nodos: NULL vale 0 y una hoja vale 1. El main calcula las consultas "
                "exitosas, incluidas repeticiones, sin imprimir resultados web prefabricados. "
                "El C usa NULL como hoja negra; el backend presenta vistas NIL. "
                "Eliminar busca el entero, trasplanta el hijo o la reserva del sucesor y libera "
                "la reserva original z, sin copiar su valor sobre ella ni reservar o imprimir. "
                "El color original guardado determina la reparacion con x y x_parent; tras free "
                "los alias a z son indeterminados, aunque su direccion se reutilice. "
                "Su referencia arbol debe ser escribible y no NULL; un arbol vacio si se admite. "
                "Eliminar ausente es no-op nativo pero rechazo de aplicacion; Liberar "
                "no actualiza la raiz por valor, el caller debe asignar NULL sin leer el alias antiguo. "
                "Limpiar libera izq, der y nodo en postorden: O(n) tiempo, O(h) pila; no "
                "imprime ni reserva y no crea/libera reservas NIL. Los alias a nodos liberados "
                "son inutilizables. Repetir solo es seguro despues de asignar NULL a la raiz; "
                "las consultas o comparaciones de punteros antiguos no son una comprobacion segura. "
                "Insertar acepta enteros entre -2147483648 y 2147483647, el int de C de 32 bits; "
                "fuera de rango se rechaza antes de modificar el arbol o guardar historial, sin truncar. "
                "El main conserva las operaciones exitosas y libera al final las reservas restantes; "
                "despues asigna NULL a la raiz. Esa limpieza del caller no agrega operaciones ni printf. "
                "Insertar busca sin reservar y solo crea un nodo si el entero no existe; escribe "
                "nro, hijos NULL, padre y ROJO antes de publicar el enlace. Los cinco casos "
                "reparan por recoloreos/rotaciones; raiz negra al terminar, sin reservas NIL. "
                "El C retorna void: referencia raiz NULL, duplicado o fallo de malloc son no-op "
                "sin confirmacion impresa; la aplicacion rechaza duplicados antes de llamar. "
                "Los auxiliares de reparacion requieren su contexto y no son metodos del menu. "
                "La rotacion no cambia enteros ni colores por si sola y no certifica cada "
                "estado parcial como rojo-negro valido."
            ),
            "supported_operations": [
                "insertar",
                "eliminar",
                "buscar",
                "inorden",
                "altura",
                "validar",
                "limpiar",
            ],
            "pending_operations": [
                "El TAD no expone el detalle paso a paso de recoloreos/rotaciones.",
            ],
        },
        "binary_heap": {
            "title": "Monticulo Binario",
            "summary": (
                "Min-heap representado en arreglo y visualizado tambien como arbol casi completo. "
                "Ver arreglo copia todos los valores en su orden interno, no en orden total. "
                "El main reproducible reserva la copia segun la cantidad actual y libera esa memoria; "
                "si la reserva falla, termina sin mostrar una copia parcial. Las consultas exitosas "
                "repetidas se conservan al recargar; restaurarlas no vuelve a ejecutarlas. "
                "En Insertar y Extraer raiz identifica los intercambios que restauran la prioridad padre-hijos. "
                "Ver raiz y Ver arreglo son consultas: no intercambian ni modifican el arreglo del monticulo. "
                "En estas dos consultas, el resaltado corresponde a la instruccion ya ejecutada; "
                "retroceder cambia la observacion, no vuelve a ejecutar una operacion. Ver raiz separa "
                "el bool de exito del int de salida, que permanece sin inicializar si falla la guarda. "
                "Ver arreglo muestra cada celda del buffer independiente al inicializarse y conserva "
                "registros anteriores a free; estos registros no son memoria viva ni punteros utilizables. "
                "Los llamadores equivalentes mostrados son auxiliares didacticos, no nuevas funciones del C/H. "
                "La capacidad es distinta de cantidad: solicitar 16 reserva 20 segun el C (base 10 y duplicacion); "
                "el elemento 21 hace crecer a 40 y extraer elementos no reduce esa capacidad. "
                "La vista muestra los valores logicos hasta cantidad; no afirma que el espacio restante sea cero. "
                "Limpiar destruye el buffer previo aunque cantidad sea cero, asigna datos NULL y luego "
                "cantidad y capacidad 0. A continuacion inicializa otro buffer: pedir 16 reserva 20 si "
                "la reserva tiene exito; si falla, conserva datos NULL, cantidad 0 y capacidad 0. "
                "El retorno void no anuncia el resultado de la reserva. La nueva vida A2 es distinta "
                "de A1 aunque el asignador reutilice una direccion. A2 nace sin enteros inicializados; "
                "las celdas fuera de cantidad en A1 se muestran como no observadas, no como ceros. "
                "Retroceder observa registros anteriores, sin ejecutar free ni reservar otra vez. "
                "En Insertar, datos[cantidad] se escribe antes del ascenso y cantidad++ ocurre despues. "
                "Los dibujos siguen las celdas escritas, incluyendo esa celda pendiente fuera de cantidad; "
                "no confunden cantidad con celdas escritas. Comparar recibe enteros por valor; intercambiar "
                "recibe alias int * y ejecuta temp=*a, *a=*b y *b=temp por separado: hay duplicacion transitoria. "
                "Division entera C trunca hacia cero: (-1)/2 da 0. El cortocircuito evita comparar si indice es 0. "
                "Si realloc crece, el buffer previo termina su vida; el nuevo conserva el prefijo y se publica "
                "antes de asignar capacidad. Entre esas instrucciones datos es indeterminado y los dibujos "
                "se suspenden. Si realloc falla, la insercion devuelve false y conserva contenido/cantidad/capacidad. "
                "El bool se muestra al retornar; avanzar o retroceder nunca vuelve a insertar. "
                "En Extraer raiz, el entero externo se escribe primero; despues disminuye cantidad. "
                "Si aun hay elementos, la antigua cola se copia en la raiz antes del descenso. "
                "Las dos vistas siguen el prefijo logico; la tarjeta de memoria conserva la cola "
                "inicializada fuera de cantidad, sin dibujarla como otro elemento. No se libera A1 "
                "ni se reduce capacidad. Cada hijo se compara solo si esta dentro de cantidad; "
                "el empate no selecciona ese hijo. El descenso muestra tres escrituras por intercambio. "
                "Si el heap esta vacio, devuelve false sin escribir salida; no hay descenso. "
                "El entero de salida es distinto del bool; retroceder no extrae de nuevo."
            ),
            "supported_operations": [
                "insertar",
                "extraer_raiz",
                "raiz",
                "a_lista",
                "limpiar",
            ],
            "pending_operations": [
                "No existe en el TAD una operacion publica para cambiar a max-heap en caliente.",
            ],
        },
    }

    _PEDAGOGY = {
        "abb": {"objective":"Decidir la rama y justificar los tres casos de eliminación.","strategy":"Comparar, descender recursivamente y reconectar el subárbol retornado.","invariant":"izquierdo < nodo < derecho en todos los nodos.","memory":"Cada nodo se reserva con malloc y se libera al eliminar o limpiar.","complexity":"O(h); promedio O(log n), peor O(n).","errors":["Confundir ABB con árbol balanceado.","Olvidar reconectar el retorno recursivo."]},
        "avl": {"objective":"Relacionar altura y FE con LL, RR, LR y RL.","strategy":"Operar como ABB, actualizar alturas y reparar el primer desequilibrio.","invariant":"Orden ABB y |FE| ≤ 1 por nodo.","memory":"Las rotaciones cambian enlaces; no crean ni destruyen nodos.","complexity":"Búsqueda, inserción y eliminación O(log n).","errors":["Rotar según el valor sin calcular FE.","No actualizar alturas después de rotar."]},
        "red_black": {"objective":"Justificar recoloreos y rotaciones con padre, abuelo y tío.","strategy":"Insertar como ABB y ejecutar casos de reparación hasta la raíz.","invariant":"Raíz negra, sin rojo-rojo y black-height uniforme.","memory":"El C representa hojas negras con NULL, sin reservas NIL. El caller libera las reservas reales y asigna NULL a su raiz; el color no sustituye los enlaces.","complexity":"Búsqueda, inserción y eliminación O(log n).","errors":["Evaluar solo el color del nodo.","Usar color sin equivalente textual."]},
        "binary_heap": {"objective":"Predecir ascenso, descenso e intercambio mediante índices.","strategy":"Mantener forma completa en arreglo y reparar prioridad padre-hijos.","invariant":"A[parent(i)] ≤ A[i] para todo i > 0.","memory":"El arreglo representa niveles; no usa enlaces de búsqueda.","complexity":"Raíz O(1), insertar y extraer O(log n).","errors":["Tratar el heap como ABB.","Esperar que el arreglo esté totalmente ordenado."]},
    }
    GLOSSARY = {
        "Raíz":"Nodo sin padre.","Hoja":"Nodo sin hijos.","Altura":"Longitud del camino máximo hacia una hoja.","Profundidad":"Distancia desde la raíz.","FE":"Diferencia de alturas entre subárboles.","Rotación":"Cambio local de enlaces que conserva el orden.","Recoloreo":"Cambio de colores para reparar reglas rojo-negro.","Black-height":"Cantidad de nodos negros por camino hasta NIL.","Heapify":"Proceso de restaurar la propiedad de heap.",
    }

    @staticmethod
    def get_module_help() -> dict[str, Any]:
        """Return the didactic help for hierarchical module."""
        return HierarchicalHelpService._MODULE_HELP

    @staticmethod
    def get_structure_help(structure_id: str) -> dict[str, Any]:
        """Return help for one hierarchical structure."""
        result=deepcopy(HierarchicalHelpService._STRUCTURE_HELP.get(
            structure_id,
            {
                "title": "Estructura no encontrada",
                "summary": "No hay ayuda disponible para esta estructura.",
                "supported_operations": [],
                "pending_operations": [],
            },
        ))
        result["pedagogy"]=deepcopy(HierarchicalHelpService._PEDAGOGY.get(structure_id,{}))
        result["glossary"]=deepcopy(HierarchicalHelpService.GLOSSARY)
        return result
