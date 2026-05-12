# PSEUDOCODIGOS TAD (REFERENCIA HISTORICA)

## Convenciones

- Este documento se conserva como referencia de diseno inicial.
- La app actual usa dos fuentes didacticas:
  - `app/services/c_code_service.py` (prioridad para modulos con cobertura C real).
  - `app/services/pseudocode_service.py` (fallback para estructuras sin cobertura C).
- Este archivo no describe toda la salida actual de UI en modulos C-first.
- `Error("...")` representa una validacion fallida.
- Regla actual de tipos: en TAD con nodos, `valor/dato` se valida como entero.
- En grafos, los vertices (`vertice`, `origen`, `destino`, `inicio`, `fin`) tambien se validan como enteros.
- En `ListaEnlazada`, la UI usa posicion desde 1 y el TAD interno usa indice desde 0.

---

## 1) PILA

### Estructura del TAD

```text
Registro Nodo
    valor
    siguiente
FinRegistro

Registro Pila
    cima : Nodo
    tam : Entero
FinRegistro
```

SubProceso Apilar(valor)
    Si valor == "" Entonces
        Error("Valor obligatorio")
    FinSi
    InsertarInicio(listaInterna, valor)
FinSubProceso

SubProceso desapilar = Desapilar()
    Si EstaVacia(listaInterna) Entonces
        Error("Pila vacia")
    FinSi
    desapilar = EliminarInicio(listaInterna)
FinSubProceso

SubProceso cima = Cima()
    Si EstaVacia(listaInterna) Entonces
        Error("Pila vacia")
    FinSi
    cima = Primero(listaInterna)
FinSubProceso

SubProceso LimpiarPila()
    Limpiar(listaInterna)
FinSubProceso

---

## 2) COLA

### Estructura del TAD

```text
Registro Nodo
    valor
    siguiente
FinRegistro

Registro Cola
    frente : Nodo
    final  : Nodo
    tam    : Entero
FinRegistro
```

SubProceso Encolar(valor)
    Si valor == "" Entonces
        Error("Valor obligatorio")
    FinSi
    InsertarFinal(listaInterna, valor)
FinSubProceso

SubProceso desencolado = Desencolar()
    Si EstaVacia(listaInterna) Entonces
        Error("Cola vacia")
    FinSi
    desencolado = EliminarInicio(listaInterna)
FinSubProceso

SubProceso frente = Frente()
    Si EstaVacia(listaInterna) Entonces
        Error("Cola vacia")
    FinSi
    frente = Primero(listaInterna)
FinSubProceso

SubProceso final = Final()
    Si EstaVacia(listaInterna) Entonces
        Error("Cola vacia")
    FinSi
    final = Ultimo(listaInterna)
FinSubProceso

SubProceso LimpiarCola()
    Limpiar(listaInterna)
FinSubProceso

---

## 3) COLA DE PRIORIDAD

### Estructura del TAD

```text
Registro ItemPrioridad
    valor
    prioridad : Entero
FinRegistro

Registro ColaPrioridad
    items : Lista de ItemPrioridad  # ordenada por prioridad ascendente
FinRegistro
```

SubProceso EncolarConPrioridad(valor, prioridad)
    Si valor == "" Entonces
        Error("Valor obligatorio")
    FinSi
    Si No EsEntero(prioridad) Entonces
        Error("Prioridad invalida")
    FinSi
    InsertarOrdenadoPorPrioridad(colaP, valor, prioridad)
FinSubProceso

SubProceso atendido = DesencolarPrioridad()
    Si EstaVacia(colaP) Entonces
        Error("Cola de prioridad vacia")
    FinSi
    atendido = ExtraerPrimero(colaP)
FinSubProceso

SubProceso frenteP = FrentePrioridad()
    Si EstaVacia(colaP) Entonces
        Error("Cola de prioridad vacia")
    FinSi
    frenteP = VerPrimero(colaP)
FinSubProceso

SubProceso LimpiarColaPrioridad()
    Limpiar(colaP)
FinSubProceso

---

## 4) LISTA ENLAZADA

### Estructura del TAD

```text
Registro Nodo
    valor
    siguiente : Nodo
FinRegistro

Registro ListaEnlazada
    cabeza : Nodo
    cola   : Nodo
    tam    : Entero
FinRegistro
```

SubProceso InsertarInicioLE(valor)
    CrearNodo(nuevo, valor)
    nuevo.siguiente = cabeza
    cabeza = nuevo
    Si cola == NULO Entonces
        cola = nuevo
    FinSi
    tam = tam + 1
FinSubProceso

SubProceso InsertarFinalLE(valor)
    CrearNodo(nuevo, valor)
    Si cola == NULO Entonces
        cabeza = nuevo
        cola = nuevo
    SiNo
        cola.siguiente = nuevo
        cola = nuevo
    FinSi
    tam = tam + 1
FinSubProceso

SubProceso InsertarPosicionLE(valor, posicionUI)
    Si posicionUI < 1 Entonces
        Error("La posicion inicia en 1")
    FinSi
    posicion = posicionUI - 1

    Si posicion < 0 O posicion > tam Entonces
        Error("Posicion fuera de rango")
    FinSi

    Si posicion == 0 Entonces
        InsertarInicioLE(valor)
        Retornar
    FinSi

    Si posicion == tam Entonces
        InsertarFinalLE(valor)
        Retornar
    FinSi

    anterior = NodoEn(posicion - 1)
    CrearNodo(nuevo, valor)
    nuevo.siguiente = anterior.siguiente
    anterior.siguiente = nuevo
    tam = tam + 1
FinSubProceso

SubProceso eliminado = EliminarPosicionLE(posicionUI)
    Si posicionUI < 1 Entonces
        Error("La posicion inicia en 1")
    FinSi
    posicion = posicionUI - 1

    Si posicion < 0 O posicion >= tam Entonces
        Error("Posicion fuera de rango")
    FinSi

    Si posicion == 0 Entonces
        eliminado = EliminarInicioLE()
        Retornar
    FinSi

    anterior = NodoEn(posicion - 1)
    objetivo = anterior.siguiente
    anterior.siguiente = objetivo.siguiente

    Si objetivo == cola Entonces
        cola = anterior
    FinSi

    tam = tam - 1
    eliminado = objetivo.valor
FinSubProceso

SubProceso posiciones = BuscarPosicionesLE(valor)
    posiciones = []
    i = 0
    actual = cabeza
    Mientras actual != NULO Hacer
        Si actual.valor == valor Entonces
            Agregar(posiciones, i + 1)
        FinSi
        actual = actual.siguiente
        i = i + 1
    FinMientras
FinSubProceso

---

## 5) LISTA CIRCULAR

### Estructura del TAD

```text
Registro NodoCircular
    valor
    siguiente : NodoCircular
FinRegistro

Registro ListaCircular
    cabeza : NodoCircular
    cola   : NodoCircular
    tam    : Entero
FinRegistro
```

SubProceso InsertarInicioLC(valor)
    CrearNodo(nuevo, valor)
    Si cabeza == NULO Entonces
        cabeza = nuevo
        cola = nuevo
        nuevo.siguiente = nuevo
    SiNo
        nuevo.siguiente = cabeza
        cabeza = nuevo
        cola.siguiente = cabeza
    FinSi
    tam = tam + 1
FinSubProceso

SubProceso InsertarFinalLC(valor)
    CrearNodo(nuevo, valor)
    Si cabeza == NULO Entonces
        cabeza = nuevo
        cola = nuevo
        nuevo.siguiente = nuevo
    SiNo
        nuevo.siguiente = cabeza
        cola.siguiente = nuevo
        cola = nuevo
    FinSi
    tam = tam + 1
FinSubProceso

SubProceso x = EliminarInicioLC()
    Si cabeza == NULO Entonces
        Error("Lista circular vacia")
    FinSi

    Si tam == 1 Entonces
        x = cabeza.valor
        cabeza = NULO
        cola = NULO
    SiNo
        x = cabeza.valor
        cabeza = cabeza.siguiente
        cola.siguiente = cabeza
    FinSi

    tam = tam - 1
FinSubProceso

SubProceso posiciones = BuscarPosicionesLC(valor)
    posiciones = []
    Si cabeza == NULO Entonces
        Retornar
    FinSi

    actual = cabeza
    i = 0
    Repetir
        Si actual.valor == valor Entonces
            Agregar(posiciones, i)
        FinSi
        actual = actual.siguiente
        i = i + 1
    Hasta Que actual == cabeza
FinSubProceso

---

## 6) SUBLISTA

### Estructura del TAD

```text
Registro Padre
    valor
    hijos : ListaEnlazada
FinRegistro

Registro Sublista
    padres : ListaEnlazada de Padre
    tamPadres : Entero
FinRegistro
```

SubProceso InsertarPadre(parent)
    Si ExistePadre(parent) Entonces
        Error("Padre duplicado")
    FinSi
    CrearPadre(parent)
    AgregarPadreAlFinal(parent)
FinSubProceso

SubProceso InsertarHijo(parent, child)
    p = BuscarPadre(parent)
    Si p == NULO Entonces
        Error("Padre no existe")
    FinSi
    AgregarHijoFinal(p, child)
FinSubProceso

SubProceso EliminarPadre(parent)
    p = BuscarPadre(parent)
    Si p == NULO Entonces
        Error("Padre no existe")
    FinSi
    BorrarPadreYSublista(p)
FinSubProceso

SubProceso hijos = HijosDe(parent)
    p = BuscarPadre(parent)
    Si p == NULO Entonces
        Error("Padre no existe")
    FinSi
    hijos = CopiarListaHijos(p)
FinSubProceso

---

## 7) ABB

### Estructura del TAD

```text
Registro NodoABB
    valor
    izq : NodoABB
    der : NodoABB
FinRegistro

Registro ABB
    raiz : NodoABB
FinRegistro
```

SubProceso InsertarABB(valor)
    Si raiz == NULO Entonces
        raiz = NuevoNodo(valor)
        Retornar
    FinSi

    actual = raiz
    Mientras VERDADERO Hacer
        Si valor < actual.valor Entonces
            Si actual.izq == NULO Entonces
                actual.izq = NuevoNodo(valor)
                Salir
            SiNo
                actual = actual.izq
            FinSi
        SiNo
            Si actual.der == NULO Entonces
                actual.der = NuevoNodo(valor)
                Salir
            SiNo
                actual = actual.der
            FinSi
        FinSi
    FinMientras
FinSubProceso

SubProceso existe = BuscarABB(valor)
    actual = raiz
    existe = FALSO
    Mientras actual != NULO Hacer
        Si valor == actual.valor Entonces
            existe = VERDADERO
            Salir
        FinSi
        Si valor < actual.valor Entonces
            actual = actual.izq
        SiNo
            actual = actual.der
        FinSi
    FinMientras
FinSubProceso

SubProceso EliminarABB(valor)
    """Caso hoja, un hijo o dos hijos (sucesor inorden)."""
FinSubProceso

---

## 8) AVL

### Estructura del TAD

```text
Registro NodoAVL
    valor
    izq : NodoAVL
    der : NodoAVL
    altura : Entero
FinRegistro

Registro AVL
    raiz : NodoAVL
FinRegistro
```

SubProceso InsertarAVL(valor)
    InsertarComoBST(valor)
    RecalcularAlturasYFE()
    Si HayDesbalance() Entonces
        AplicarRotacion(LL/RR/LR/RL)
    FinSi
FinSubProceso

SubProceso EliminarAVL(valor)
    EliminarComoBST(valor)
    RecalcularAlturasYFE()
    Si HayDesbalance() Entonces
        AplicarRotacion(LL/RR/LR/RL)
    FinSi
FinSubProceso

SubProceso valida = ValidarAVL()
    valida = TodosLosNodosCumplenFE(-1, 0, 1)
FinSubProceso

---

## 9) ROJO-NEGRO

### Estructura del TAD

```text
Registro NodoRN
    valor
    color : {ROJO, NEGRO}
    izq : NodoRN
    der : NodoRN
    padre : NodoRN
FinRegistro

Registro ArbolRN
    raiz : NodoRN
FinRegistro
```

SubProceso InsertarRN(valor)
    InsertarComoBSTColorRojo(valor)
    RepararPropiedadesRN()
    raiz.color = NEGRO
FinSubProceso

SubProceso EliminarRN(valor)
    EliminarNodoBST(valor)
    RepararPropiedadesRNPostEliminacion()
FinSubProceso

SubProceso valida = ValidarRN()
    valida = CumplePropiedadesRojoNegro()
FinSubProceso

---

## 10) MONTICULO BINARIO

### Estructura del TAD

```text
Registro MonticuloBinario
    arreglo : Arreglo dinamico
    tam : Entero
FinRegistro
```

SubProceso InsertarHeap(valor)
    AgregarFinal(arreglo, valor)
    SiftUp(arreglo, UltimoIndice(arreglo))
FinSubProceso

SubProceso raiz = ExtraerRaizHeap()
    Si Longitud(arreglo) == 0 Entonces
        Error("Monticulo vacio")
    FinSi

    raiz = arreglo[0]
    arreglo[0] = Ultimo(arreglo)
    QuitarUltimo(arreglo)
    SiftDown(arreglo, 0)
FinSubProceso

---

## 11) GRAFO

### Estructura del TAD

```text
Registro Arista
    destino
    peso : Real
FinRegistro

Registro Grafo
    dirigido : Logico
    ady : Diccionario<Vertice, Lista de Arista>
FinRegistro
```

SubProceso CrearGrafo(esDirigido)
    dirigido = esDirigido
    ady = DiccionarioVacio()
FinSubProceso

SubProceso InsertarVertice(v)
    Si No ExisteClave(ady, v) Entonces
        ady[v] = ListaVacia()
    FinSi
FinSubProceso

SubProceso InsertarArista(u, v, w)
    InsertarVertice(u)
    InsertarVertice(v)
    AgregarArista(ady, u, v, w)
    Si NO dirigido Entonces
        AgregarArista(ady, v, u, w)
    FinSi
FinSubProceso

SubProceso orden = BFS(inicio)
    ValidarVertice(inicio)
    cola = [inicio]
    visitado = {inicio}
    orden = []

    Mientras NoVacia(cola) Hacer
        x = Desencolar(cola)
        Agregar(orden, x)
        ParaCada y En Vecinos(x) Hacer
            Si y NoEn visitado Entonces
                Agregar(visitado, y)
                Encolar(cola, y)
            FinSi
        FinPara
    FinMientras
FinSubProceso

SubProceso orden = DFS(inicio)
    ValidarVertice(inicio)
    pila = [inicio]
    visitado = {}
    orden = []

    Mientras NoVacia(pila) Hacer
        x = Desapilar(pila)
        Si x NoEn visitado Entonces
            Agregar(visitado, x)
            Agregar(orden, x)
            ParaCada y En VecinosEnOrdenInverso(x) Hacer
                Si y NoEn visitado Entonces
                    Apilar(pila, y)
                FinSi
            FinPara
        FinSi
    FinMientras
FinSubProceso

SubProceso resultado = Dijkstra(inicio, destino)
    Si ExistePesoNegativo() Entonces
        Error("Dijkstra no admite pesos negativos")
    FinSi
    InicializarDistancias(infinito)
    dist[inicio] = 0
    pq = ColaPrioridad()
    Encolar(pq, (0, inicio))

    Mientras NoVacia(pq) Hacer
        (d, u) = ExtraerMin(pq)
        Si d > dist[u] Entonces
            Continuar
        FinSi
        ParaCada (v, w) En AristasDesde(u) Hacer
            Si dist[u] + w < dist[v] Entonces
                dist[v] = dist[u] + w
                prev[v] = u
                Encolar(pq, (dist[v], v))
            FinSi
        FinPara
    FinMientras

    resultado = ReconstruirRutaYDistancia(prev, dist, inicio, destino)
FinSubProceso

SubProceso resultado = BellmanFord(inicio, destino)
    InicializarDistancias(infinito)
    dist[inicio] = 0

    Para i = 1 Hasta CantVertices() - 1 Hacer
        ParaCada (u, v, w) En TodasLasAristas() Hacer
            Si dist[u] + w < dist[v] Entonces
                dist[v] = dist[u] + w
                prev[v] = u
            FinSi
        FinPara
    FinPara

    resultado = ReconstruirRutaYDistancia(prev, dist, inicio, destino)
FinSubProceso

SubProceso mst = Prim(inicio)
    Si dirigido Entonces
        Error("Prim requiere grafo no dirigido")
    FinSi
    """Expandir MST desde inicio tomando arista minima valida."""
FinSubProceso

SubProceso mst = Kruskal()
    Si dirigido Entonces
        Error("Kruskal requiere grafo no dirigido")
    FinSi
    OrdenarAristasPorPeso()
    InicializarUnionFind()
    ParaCada arista En aristasOrdenadas Hacer
        Si Union(arista.u, arista.v) Entonces
            AgregarAristaMST(arista)
        FinSi
    FinPara
FinSubProceso

---

## 12) UNION-FIND (SOPORTE KRUSKAL)

### Estructura del TAD

```text
Registro UnionFind
    parent : Diccionario<Vertice, Vertice>
    rank   : Diccionario<Vertice, Entero>
FinRegistro
```

SubProceso MakeSet(x)
    parent[x] = x
    rank[x] = 0
FinSubProceso

SubProceso r = Find(x)
    Si parent[x] != x Entonces
        parent[x] = Find(parent[x])
    FinSi
    r = parent[x]
FinSubProceso

SubProceso unido = Union(x, y)
    rx = Find(x)
    ry = Find(y)
    Si rx == ry Entonces
        unido = FALSO
        Retornar
    FinSi
    Si rank[rx] < rank[ry] Entonces
        parent[rx] = ry
    SiNo
        Si rank[rx] > rank[ry] Entonces
            parent[ry] = rx
        SiNo
            parent[ry] = rx
            rank[rx] = rank[rx] + 1
        FinSi
    FinSi
    unido = VERDADERO
FinSubProceso

---

## 13) TABLA HASH

### Estructura del TAD

```text
Registro ParClaveValor
    clave
    valor
FinRegistro

Registro TablaHash
    buckets : Arreglo de Lista de ParClaveValor
    capacidad : Entero
    size : Entero
FinRegistro
```

SubProceso CrearTabla(capacidad)
    Si capacidad <= 0 Entonces
        Error("Capacidad invalida")
    FinSi
    buckets = ArregloDeListas(capacidad)
    size = 0
FinSubProceso

SubProceso resultado = InsertarHash(clave, valor)
    i = Hash(clave) MOD capacidad
    Si ExisteClaveEnBucket(buckets[i], clave) Entonces
        ActualizarValor(buckets[i], clave, valor)
        resultado.actualizado = VERDADERO
    SiNo
        AgregarPar(buckets[i], clave, valor)
        size = size + 1
        resultado.actualizado = FALSO
    FinSi

    Si FactorCarga(size, capacidad) > UMBRAL Entonces
        RedimensionarYRehash()
        resultado.redimension = VERDADERO
    FinSi
FinSubProceso

SubProceso valor = BuscarHash(clave)
    i = Hash(clave) MOD capacidad
    valor = ObtenerValorOBNulo(buckets[i], clave)
FinSubProceso

SubProceso existe = ContieneHash(clave)
    valor = BuscarHash(clave)
    existe = (valor != NULO)
FinSubProceso

SubProceso eliminado = EliminarHash(clave)
    i = Hash(clave) MOD capacidad
    eliminado = EliminarParSiExiste(buckets[i], clave)
    Si eliminado Entonces
        size = size - 1
    FinSi
FinSubProceso

SubProceso LimpiarHash()
    Para i = 0 Hasta capacidad - 1 Hacer
        buckets[i] = ListaVacia()
    FinPara
    size = 0
FinSubProceso

SubProceso estadisticas = StatsHash()
    estadisticas.size = size
    estadisticas.capacity = capacidad
    estadisticas.factor = size / capacidad
FinSubProceso


