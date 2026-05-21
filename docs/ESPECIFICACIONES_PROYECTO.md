# Especificaciones del Proyecto - Visualizador Web de Estructuras de Datos
**Documento Base para Software Design Document (SDD)**

**Última Actualización:** 18 de mayo de 2026  
**Versión:** 1.0  
**Estado:** Activo  
**Entorno de Validación:** Python 3.10.5 (Windows)

---

## Tabla de Contenidos

1. [Propósito y Visión General](#1-propósito-y-visión-general)
2. [Alcance](#2-alcance)
3. [Requisitos Funcionales](#3-requisitos-funcionales)
4. [Requisitos No Funcionales](#4-requisitos-no-funcionales)
5. [Arquitectura General del Sistema](#5-arquitectura-general-del-sistema)
6. [Componentes Principales](#6-componentes-principales)
7. [Módulos y Estructuras de Datos](#7-módulos-y-estructuras-de-datos)
8. [Especificaciones de Interfaz](#8-especificaciones-de-interfaz)
9. [Especificaciones de API REST](#9-especificaciones-de-api-rest)
10. [Especificaciones de Seguridad](#10-especificaciones-de-seguridad)
11. [Especificaciones de Configuración](#11-especificaciones-de-configuración)
12. [Especificaciones de Gestión de Sesiones](#12-especificaciones-de-gestión-de-sesiones)
13. [Especificaciones de Base de Datos](#13-especificaciones-de-base-de-datos)
14. [Métricas de Calidad](#14-métricas-de-calidad)
15. [Comportamiento de Ejecución e Interpretación](#15-comportamiento-de-ejecución-e-interpretación)
16. [Reglas de Validación de Entrada](#16-reglas-de-validación-de-entrada)
17. [Flujos de Casos de Uso](#17-flujos-de-casos-de-uso)
18. [Endpoints Principales](#18-endpoints-principales)

---

## 1. Propósito y Visión General

### 1.1 Propósito
Proporcionar una aplicación web didáctica interactiva que permita a estudiantes y profesionales practicar y visualizar el comportamiento de Tipos Abstractos de Datos (TAD) mediante una interfaz gráfica intuitiva, integrada con código C real basado en los TAD nuevos definidos en `docs/tads_C`.

### 1.2 Visión
Ser una herramienta educativa integral que combine:
- Visualización interactiva de estructuras de datos
- Interpretación gráfica de código C en tiempo real
- Simulación paso a paso de algoritmos
- Retroalimentación didáctica inmediata
- Coherencia total entre código, visualización y estado

### 1.3 Público Objetivo
- Estudiantes de estructuras de datos
- Profesionales en formación o especialización
- Docentes para demostración en clase
- Comunidad académica general

### 1.4 Contexto Técnico
- Framework: Flask 3.1.0
- Lenguaje: Python 3.10+
- Plataforma: Windows 10/11 con navegador moderno
- Versión de Referencia C: TAD nuevos en `docs/tads_C`

---

## 2. Alcance

### 2.1 Dentro del Alcance
- Cuatro módulos principales de estructuras: Secuencial, Jerárquico, Grafos y Hash
- 13 estructuras de datos diferentes
- Visualización interactiva del estado interno
- Integración con código C y pseudocódigo
- Simulación paso a paso
- Gestión de sesiones server-side
- Suite de pruebas automatizada (274 casos)
- Documentación completa de usuario

### 2.2 Fuera del Alcance
- Soporte para TAD legacy (nombres como `rn_*`, `struct Abb`)
- Compilación de código C en el servidor
- Bases de datos persistentes externas
- Análisis de complejidad automático
- Generación de reportes académicos

### 2.3 Limitaciones Conocidas
- Ejecución local limitada a `127.0.0.1:5050` por defecto
- Máximo 300 operaciones en historial por sesión
- Máximo 10,000 sesiones en caché filesystem
- Dependencia de navegador para renderización

---

## 3. Requisitos Funcionales

### 3.1 Gestión de Estructuras de Datos
**RF-3.1.1:** El sistema debe permitir crear instancias de 13 estructuras de datos diferentes.  
**RF-3.1.2:** El sistema debe permitir ejecutar operaciones sobre cada estructura con validación de entrada.  
**RF-3.1.3:** El sistema debe permitir reiniciar o limpiar el estado de cualquier estructura.  
**RF-3.1.4:** El sistema debe mantener un registro histórico de operaciones por sesión (máximo 300).

### 3.2 Módulo Secuencial
**RF-3.2.1:** Implementar y visualizar: Pila, Cola, Cola de Prioridad, Lista Enlazada, Lista Circular, Sublista.  
**RF-3.2.2:** Soportar operaciones de inserción, eliminación, búsqueda y limpieza.  
**RF-3.2.3:** Mostrar código C para cada operación desde `docs/tads_C`.  
**RF-3.2.4:** Permitir interpretación paso a paso con controles Anterior/Siguiente.

### 3.3 Módulo Jerárquico
**RF-3.3.1:** Implementar y visualizar: ABB, AVL, Rojo-Negro, Montículo Binario.  
**RF-3.3.2:** Soportar operaciones de inserción, eliminación, búsqueda y limpieza.  
**RF-3.3.3:** Mostrar código C para cada operación.  
**RF-3.3.4:** Visualizar rotaciones y rebalanceo automáticamente.

### 3.4 Módulo de Grafos
**RF-3.4.1:** Implementar grafos dirigidos y no dirigidos.  
**RF-3.4.2:** Soportar operaciones: agregar vértice/arista, recorridos (BFS/DFS), camino mínimo (Dijkstra), árbol expansión mínima (Kruskal/Prim).  
**RF-3.4.3:** Integrar simulación en fase "Paso 3: Ejecutar algoritmo".  
**RF-3.4.4:** Mostrar estado visual actualizado en modo rápido equivalente al modo interpretado.

### 3.5 Módulo Hash
**RF-3.5.1:** Implementar tabla hash con manejo de colisiones.  
**RF-3.5.2:** Soportar operaciones: inserción, búsqueda, eliminación, estadísticas.  
**RF-3.5.3:** Mostrar código C desde `docs/tads_C`.  
**RF-3.5.4:** Visualizar distribución de claves en la tabla.

### 3.6 Simulación Didáctica
**RF-3.6.1:** La simulación debe ser un intérprete gráfico de código C, no una reproducción lineal.  
**RF-3.6.2:** Respetar estructuras de control (if/else, while, for, switch): solo animar ramas ejecutadas.  
**RF-3.6.3:** En operaciones mutantes, mostrar: estado inicial → estructura temporal → asignaciones intermedias → reasignación → estado final.  
**RF-3.6.4:** Sincronizar resaltado de código C con animación visual en cada paso.  
**RF-3.6.5:** Mostrar salida de printf() coherente con la ruta de ejecución real.  
**RF-3.6.6:** Mantener historial como programa principal (main) coherente.

### 3.7 Apoyo Didáctico
**RF-3.7.1:** Mostrar estructura del TAD (record C) en interfaz.  
**RF-3.7.2:** Mostrar código C específico para cada operación.  
**RF-3.7.3:** Proporcionar fallback con pseudocódigo cuando no exista mapeo C.  
**RF-3.7.4:** Ofrecer mensajes de error didácticos en español.

### 3.8 Navegación y Usabilidad
**RF-3.8.1:** Barra de navegación con acceso a: Inicio, Secuencial, Jerárquico, Grafos, Hash, Ayuda.  
**RF-3.8.2:** Interfaz adaptativa para cada módulo.  
**RF-3.8.3:** Formularios dinámicos basados en operación seleccionada.  
**RF-3.8.4:** Visualización en tiempo real del estado de la estructura.

### 3.9 Gestión de Sesiones
**RF-3.9.1:** Crear y mantener sesiones server-side con duración configurable (defecto 240 minutos).  
**RF-3.9.2:** Almacenar estado de estructuras por sesión.  
**RF-3.9.3:** Soportar backend cachelib (filesystem) y Redis.  
**RF-3.9.4:** Renovar sesión en cada solicitud si está configurado.

### 3.10 Healthcheck
**RF-3.10.1:** Proporcionar endpoint `/healthz` que retorne status de salud del servidor.

---

## 4. Requisitos No Funcionales

### 4.1 Rendimiento
**RNF-4.1.1:** Latencia máxima en operación simple: 200ms.  
**RNF-4.1.2:** Carga de página principal: < 1 segundo.  
**RNF-4.1.3:** Soportar mínimo 100 sesiones concurrentes en cachelib.  
**RNF-4.1.4:** Máximo 10,000 sesiones en caché filesystem.  
**RNF-4.1.5:** Simulación paso a paso debe avanzar sin lag perceptible (< 50ms por paso).

### 4.2 Disponibilidad
**RNF-4.2.1:** Uptime esperado: 99% en producción.  
**RNF-4.2.2:** Recuperación automática ante fallos de conexión a Redis.  
**RNF-4.2.3:** Degradación segura a cachelib si Redis no está disponible.

### 4.3 Escalabilidad
**RNF-4.3.1:** Arquitectura preparada para frontend escalable (SPA).  
**RNF-4.3.2:** API REST stateless para endpoints de operaciones.  
**RNF-4.3.3:** Sesiones escalables mediante Redis en producción.  
**RNF-4.3.4:** Soportar arquitecturas con múltiples instancias detrás de reverse proxy.

### 4.4 Seguridad
**RNF-4.4.1:** Todas las sesiones requieren `SECRET_KEY` segura en producción.  
**RNF-4.4.2:** Cookies con flags: `HttpOnly=True`, `SameSite=Lax` por defecto.  
**RNF-4.4.3:** Soporte para HTTPS mediante `SESSION_COOKIE_SECURE=True`.  
**RNF-4.4.4:** Validación y sanitización de todas las entradas.  
**RNF-4.4.5:** Prevención de CSRF mediante tokens de sesión.  
**RNF-4.4.6:** Soporte para ProxyFix cuando se ejecuta detrás de reverse proxy.

### 4.5 Usabilidad
**RNF-4.5.1:** Interfaz en español.  
**RNF-4.5.2:** Mensajes de error claros y didácticos.  
**RNF-4.5.3:** Tiempo de aprendizaje < 15 minutos para usuarios objetivo.  
**RNF-4.5.4:** Accesibilidad básica (contraste, tamaño de fuente).

### 4.6 Mantenibilidad
**RNF-4.6.1:** Cobertura de pruebas: mínimo 85% (objetivo actual: 85%).  
**RNF-4.6.2:** Código modular con responsabilidad única por clase.  
**RNF-4.6.3:** Documentación inline en código.  
**RNF-4.6.4:** Separación clara de capas (domain, adapters, services, routes).

### 4.7 Compatibilidad
**RNF-4.7.1:** Python 3.10+  
**RNF-4.7.2:** Windows 10/11  
**RNF-4.7.3:** Navegadores modernos (Chrome, Firefox, Edge, Safari últimas 3 versiones)  
**RNF-4.7.4:** Alineación total con TAD nuevos en `docs/tads_C` (sin soporte legacy)

### 4.8 Testabilidad
**RNF-4.8.1:** Suite automatizada: mínimo 274 casos.  
**RNF-4.8.2:** Pruebas unitarias, integración y E2E.  
**RNF-4.8.3:** Ejecutables con `pytest` en un solo comando.  
**RNF-4.8.4:** CI/CD ready.

---

## 5. Arquitectura General del Sistema

### 5.1 Patrón de Diseño
**Patrón MVC + Adaptador + Servicio**
- **Vista (V):** Templates Jinja2 + CSS/JS en `templates/` y `static/`
- **Controlador (C):** Blueprints Flask en `app/routes/`
- **Modelo (M):** Domain objects en `app/domain/` + Adapters en `app/adapters/`
- **Servicios:** Lógica de negocio en `app/services/`

### 5.2 Capas Lógicas

```
┌─────────────────────────────────────┐
│      Presentación (Templates)       │
│     CSS/JS (static/)                │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    API REST (Flask Routes)          │
│ (sequential_routes.py, etc.)        │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    Servicios Orquestadores          │
│  (structure_service, session_service) │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    Adaptadores de Estructura        │
│  (StackAdapter, TreeAdapter, etc.)  │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│    Domain Objects (Implementaciones)│
│  (Stack, Queue, LinkedList, etc.)   │
└─────────────────────────────────────┘
```

### 5.3 Flujo de Solicitud General

1. **Cliente** → Envía solicitud HTTP (GET/POST)
2. **Route Handler** → Recibe en blueprint específico
3. **Session Service** → Recupera/crea sesión
4. **Structure Service** → Busca estructura y estado
5. **Adapter** → Ejecuta operación sobre structure
6. **Visual Service** → Genera estado visual
7. **Template/JSON** → Retorna respuesta
8. **Cliente** → Renderiza en UI

### 5.4 Inicialización de la Aplicación

```python
# app/__init__.py
create_app()
  ├── Configuración (Config)
  ├── Session backend (cachelib/redis)
  ├── ProxyFix (si ENABLE_PROXY_FIX=True)
  └── Blueprints registrados:
      ├── main_bp
      ├── sequential_bp
      ├── hierarchical_bp
      ├── graph_bp
      ├── hash_bp
      └── help_bp
```

---

## 6. Componentes Principales

### 6.1 Estructura de Directorios

```
app/
├── __init__.py                    # Application factory
├── config.py                      # Configuración
├── adapters/                      # Contrato común BaseAdapter
│   ├── base_adapter.py
│   ├── stack_adapter.py
│   ├── queue_adapter.py
│   ├── priority_queue_adapter.py
│   ├── linked_list_adapter.py
│   ├── circular_list_adapter.py
│   ├── sublist_adapter.py
│   ├── abb_adapter.py
│   ├── avl_adapter.py
│   ├── red_black_adapter.py
│   ├── binary_heap_adapter.py
│   ├── graph_adapter.py
│   └── hash_table_adapter.py
├── domain/                        # Implementaciones de TAD
│   ├── sequential/
│   │   ├── stack.py
│   │   ├── queue.py
│   │   ├── priority_queue.py
│   │   ├── linked_list.py
│   │   ├── circular_list.py
│   │   └── sublist.py
│   ├── hierarchical/
│   │   ├── abb.py
│   │   ├── avl.py
│   │   ├── red_black.py
│   │   └── binary_heap.py
│   ├── graph/
│   │   └── graph.py
│   └── hash/
│       └── hash_table.py
├── routes/                        # Flask Blueprints
│   ├── main_routes.py            # / /healthz /assets
│   ├── sequential_routes.py
│   ├── hierarchical_routes.py
│   ├── graph_routes.py
│   ├── hash_routes.py
│   └── help_routes.py
├── services/                      # Orquestadores
│   ├── structure_service.py      # Gestión de estructuras
│   ├── session_service.py        # Gestión de sesiones
│   ├── c_code_service.py         # Mapeo de código C
│   ├── pseudocode_service.py     # Fallback pseudocódigo
│   ├── execution_trace_service.py # Traza de ejecución
│   ├── help_service.py           # Contenido de ayuda
│   ├── hierarchical_help_service.py
│   ├── hash_help_service.py
│   ├── hash_structure_service.py
│   ├── hierarchical_structure_service.py
│   ├── graph_help_service.py
│   └── graph_structure_service.py
templates/                         # Vistas Jinja2
├── base.html
├── index.html
├── _navbar.html
├── _header.html
├── _footer.html
├── sequential/
├── hierarchical/
├── graph/
└── hash/
static/                            # Assets
├── css/
│   ├── style.css
│   └── ...
└── js/
    ├── app.js
    ├── visualization.js
    └── ...
```

### 6.2 Contrato de BaseAdapter

Cada adapter implementa la interfaz abstracta `BaseAdapter`:

```python
class BaseAdapter(ABC):
    def create(self) -> None:
        """Crear o recrear la instancia de estructura."""
    
    def execute(self, operation_name: str, payload: dict) -> dict:
        """Ejecutar operación con validación."""
    
    def to_visual_state(self) -> dict:
        """Retornar estado serializable para UI."""
    
    def reset(self) -> None:
        """Limpiar estado."""
    
    def get_supported_operations(self) -> list[dict]:
        """Retornar metadatos de operaciones soportadas."""
```

### 6.3 Factory Pattern para Adapters

```python
# app/services/structure_service.py
def get_adapter(structure_type: str, adapter_type: str) -> BaseAdapter:
    """Obtener adapter según tipo de estructura."""
    # Mapeo: structure_type → adapter correspondiente
    adapters = {
        'stack': StackAdapter(),
        'queue': QueueAdapter(),
        # ... etc
    }
    return adapters[structure_type]
```

### 6.4 Session Service

```python
# app/services/session_service.py
- Crear sesión para cada estructura
- Almacenar estado interno
- Recuperar estado en solicitudes subsecuentes
- Backend: cachelib (default) o Redis (producción)
- Duración: 240 minutos (configurable)
- Máximo histórico: 300 operaciones
```

---

## 7. Módulos y Estructuras de Datos

### 7.1 Módulo Secuencial

| Estructura | Clase Domain | Adapter | Operaciones Soportadas |
|---|---|---|---|
| Pila | `Stack` | `StackAdapter` | push, pop, peek, isEmpty, size, clear |
| Cola | `Queue` | `QueueAdapter` | enqueue, dequeue, peek, isEmpty, size, clear |
| Cola de Prioridad | `PriorityQueue` | `PriorityQueueAdapter` | insert, extractMin, peek, isEmpty, size, clear |
| Lista Enlazada | `LinkedList` | `LinkedListAdapter` | insert, delete, search, traverse, size, clear |
| Lista Circular | `CircularList` | `CircularListAdapter` | insert, delete, search, traverse, size, clear |
| Sublista | `Sublist` | `SublistAdapter` | insert, delete, search, getSubrange, size, clear |

**Características Comunes:**
- Validación de entrada (números enteros)
- Visualización de nodos y enlaces
- Código C desde `docs/tads_C/secuencial/`
- Ejecución paso a paso

### 7.2 Módulo Jerárquico

| Estructura | Clase Domain | Adapter | Operaciones Soportadas |
|---|---|---|---|
| ABB | `ABB` | `ABBAdapter` | insert, delete, search, inorder, preorder, postorder, balanceCheck |
| AVL | `AVL` | `AVLAdapter` | insert, delete, search, inorder, preorder, postorder, rebalance |
| Rojo-Negro | `RedBlack` | `RedBlackAdapter` | insert, delete, search, inorder, preorder, postorder, recolor |
| Montículo Binario | `BinaryHeap` | `BinaryHeapAdapter` | insert, extractMin/Max, peek, size, clear, heapify |

**Características Comunes:**
- Validación de entrada (números enteros)
- Visualización de estructura jerárquica
- Mostrar rotaciones y rebalanceos
- Código C desde `docs/tads_C/jerarquico/`
- Ejecución paso a paso

### 7.3 Módulo de Grafos

**Características:**
- Grafo dirigido y no dirigido
- Vértices: números enteros
- Aristas: peso numérico (int/float)
- Fases de construcción:
  - Paso 1: Agregar vértices y aristas
  - Paso 2: Seleccionar algoritmo
  - Paso 3: Ejecutar algoritmo

**Algoritmos Soportados:**
1. **Recorridos:**
   - BFS (Breadth-First Search)
   - DFS (Depth-First Search)
   - Resultado: orden de visitación

2. **Camino Mínimo (requiere origen y destino):**
   - Dijkstra (grafos ponderados sin negativos)
   - Resultado: camino y costo

3. **Árbol de Expansión Mínima (grafos no dirigidos ponderados):**
   - Kruskal
   - Prim
   - Resultado: aristas del árbol

**Visualización:**
- Nodos resaltados según fase
- Aristas resaltadas según algoritmo
- Acción actual (Evaluando condición / Aplicando cambio)
- Modo rápido: resultado final visual
- Modo interpretado: paso a paso completo

### 7.4 Módulo Hash

| Estructura | Clase Domain | Adapter | Operaciones Soportadas |
|---|---|---|---|
| Tabla Hash | `HashTable` | `HashTableAdapter` | insert, search, delete, statistics, show |

**Características:**
- Claves: texto
- Valores: texto
- Manejo de colisiones configurable
- Visualización de tabla y distribución
- Código C desde `docs/tads_C/hash/`
- Ejecución paso a paso

---

## 8. Especificaciones de Interfaz

### 8.1 Componentes de la Interfaz

#### 8.1.1 Barra de Navegación
- Logo/Inicio
- Módulo Secuencial
- Módulo Jerárquico
- Módulo Grafos
- Módulo Hash
- Secciones de Ayuda
- Responsive design

#### 8.1.2 Página de Inicio
- Descripción del proyecto
- Acceso rápido a módulos
- Enlaces a documentación

#### 8.1.3 Interfaz de Módulo
Estructura común para todos los módulos:

```
┌──────────────────────────────────────────┐
│            Barra de Navegación           │
├────────────────┬─────────────────────────┤
│                │                         │
│  Panel de      │    Visualización        │
│  Selección     │    Principal            │
│  ├─ Estructura │    ┌─────────────────┐  │
│  ├─ Operación  │    │  Canvas/Render  │  │
│  ├─ Inputs     │    │  de Estructura  │  │
│  └─ Botones    │    └─────────────────┘  │
│                │                         │
│                ├─────────────────────────┤
│                │   Código C / Pseudocód. │
│                │   Historial / Main      │
│                │   Consola (printf)      │
│                │ Controles paso a paso   │
└────────────────┴─────────────────────────┘
```

#### 8.1.4 Panel de Selección
- Dropdown: seleccionar estructura
- Dropdown: seleccionar operación
- Formulario dinámico: inputs según operación
- Botón: Ejecutar
- Botón: Reiniciar
- Checkbox: Interpretar paso a paso

#### 8.1.5 Área de Visualización
- Canvas/SVG: representación visual de estructura
- Nodos, enlaces, valores, pesos
- Color según estado (normal, resaltado, activo)
- Animaciones suaves

#### 8.1.6 Panel de Código C
- Tabs: "Estructura del TAD" | "Código C: <Operación>"
- Syntax highlighting para C
- Línea actualmente ejecutada resaltada
- Scroll sincronizado con ejecución

#### 8.1.7 Panel de Historial
- Mostrar como "main()" de programa principal
- Línea por línea: cada operación realizada
- Estado consistente con UI visual

#### 8.1.8 Consola de Ejecución
- Mostrar salida de printf() del código C
- Solo líneas ejecutadas en la ruta actual
- Limpia al reiniciar

#### 8.1.9 Controles de Ejecución Paso a Paso
**Para Secuencial/Jerárquico/Hash:**
```
┌─────────────────────────────────────┐
│     Reproducir       Reiniciar      │  ← Fila superior
├─────────────────────────────────────┤
│  Anterior paso    Siguiente paso     │  ← Fila inferior
│  Velocidad ■───■                    │
│  Paso N de M                         │
└─────────────────────────────────────┘
```

**Para Grafos (Paso 3):**
```
┌─────────────────────────────────────┐
│  Reproducir    Anterior    Siguiente │
│  Velocidad ■───■                    │
│  Paso N de M                         │
│  Acción actual: [Evaluando|Cambio]   │
└─────────────────────────────────────┘
```

### 8.2 Flujo de Interacción

1. Usuario selecciona módulo
2. Carga lista de estructuras disponibles
3. Usuario selecciona estructura
4. Interfaz carga operaciones disponibles
5. Usuario elige operación
6. Formulario dinámico muestra inputs necesarios
7. Usuario completa inputs
8. Usuario presiona "Ejecutar"
9. Servidor simula operación paso a paso
10. UI anima cambios en estructura
11. Código C resaltado avanza sincronizado
12. Consola muestra salida de printf
13. Usuario puede:
    - Retroceder con "Anterior paso"
    - Avanzar con "Siguiente paso"
    - Reproducir automáticamente
    - Ejecutar final directo sin pasos
14. Usuario presiona "Reiniciar" para limpiar estructura

### 8.3 Temas y Estilos
- Tema oscuro/claro (configurable)
- Tipografía: sans-serif moderna
- Colores: contraste WCAG AA
- Animaciones: suaves, sin lag

---

## 9. Especificaciones de API REST

### 9.1 Convención General
- **Formato:** JSON
- **Métodos:** GET, POST
- **Códigos de Estado:** 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- **Charset:** UTF-8

### 9.2 Autenticación y Autorización
- No requiere autenticación explícita
- Sesión automática por cookies
- CSRF token implícito en sesión

### 9.3 Endpoints Principales

#### 9.3.1 Endpoints Generales

**GET /**
- Descripción: Página de inicio
- Parámetros: ninguno
- Respuesta: HTML (index.html)
- Status: 200

**GET /healthz**
- Descripción: Health check del servidor
- Parámetros: ninguno
- Respuesta: `{"status": "healthy"}`
- Status: 200

**GET /assets/<path:filename>**
- Descripción: Servir archivos estáticos
- Parámetros: `filename` (ruta del archivo)
- Respuesta: archivo CSS/JS/imagen
- Status: 200 | 404

#### 9.3.2 Endpoints Secuencial

**GET /sequential/**
- Descripción: Página módulo secuencial
- Parámetros: ninguno
- Respuesta: HTML del módulo
- Status: 200

**POST /sequential/<id>/operate**
- Descripción: Ejecutar operación en estructura secuencial
- Parámetros:
  ```json
  {
    "structure_type": "stack|queue|...",
    "operation": "push|pop|...",
    "payload": {
      "value": 10,
      "position": 0
    },
    "step_backward": false,
    "interpret_step_by_step": true
  }
  ```
- Respuesta:
  ```json
  {
    "success": true,
    "message": "Operación completada",
    "visual_state": { ... },
    "execution_trace": [ ... ],
    "current_step": 3,
    "total_steps": 5,
    "c_code_active_line": 12,
    "console_output": "...",
    "history": [ ... ]
  }
  ```
- Status: 200 | 400

**POST /sequential/<id>/reset**
- Descripción: Reiniciar estructura
- Parámetros: ninguno (en body)
- Respuesta: `{"success": true}`
- Status: 200

#### 9.3.3 Endpoints Jerárquico (Análogo a Secuencial)

**GET /hierarchical/**
**POST /hierarchical/<id>/operate**
**POST /hierarchical/<id>/reset**

Estructura de request/response idéntica a secuencial pero para estructuras jerárquicas.

#### 9.3.4 Endpoints Grafos

**GET /graph/**
- Descripción: Página del módulo grafos
- Respuesta: HTML del módulo

**GET /graph/<id>/<phase>**
- Descripción: Obtener configuración de fase específica
- Parámetros:
  - `id`: identificador de sesión
  - `phase`: construccion | recorridos | camino-minimo | expansion-minima
- Respuesta: Configuración de la fase

**POST /graph/<id>/operate**
- Descripción: Ejecutar operación en grafo
- Parámetros:
  ```json
  {
    "phase": "construction|traversal|shortest-path|mst",
    "operation": "add_vertex|add_edge|run_algorithm|...",
    "payload": {
      "vertex": 1,
      "origin": 1,
      "target": 2,
      "weight": 5.5,
      "algorithm": "dfs|bfs|dijkstra|kruskal|prim"
    }
  }
  ```
- Respuesta: Similar a secuencial con estado visual del grafo

**POST /graph/<id>/reset**
- Descripción: Reiniciar grafo

#### 9.3.5 Endpoints Hash

**GET /hash/**
**POST /hash/<id>/operate**
**POST /hash/<id>/reset**

Análogo a secuencial pero para tabla hash.

#### 9.3.6 Endpoints de Ayuda

**GET /help/<module>**
- Descripción: Obtener contenido de ayuda de módulo
- Parámetros: `module`: sequential | hierarchical | graph | hash
- Respuesta: HTML con contenido de ayuda

**GET /help/<module>/<structure>**
- Descripción: Obtener ayuda específica de estructura
- Respuesta: HTML detallado

### 9.4 Formato de Respuesta de Operación

```json
{
  "success": true,
  "message": "Operación realizada exitosamente",
  
  "visual_state": {
    "nodes": [
      {"id": 1, "value": 10, "x": 100, "y": 200, "state": "normal"},
      {"id": 2, "value": 20, "x": 200, "y": 200, "state": "highlighted"}
    ],
    "edges": [
      {"from": 1, "to": 2, "weight": null, "state": "active"}
    ],
    "temp_structures": [
      {"name": "aux", "content": "20", "position": "right"}
    ],
    "structure_type": "LinkedList",
    "size": 2
  },
  
  "execution_trace": [
    {"step": 1, "line": 5, "action": "Crear nodo aux", "state_snapshot": {...}},
    {"step": 2, "line": 6, "action": "Asignar aux->valor = 20", "state_snapshot": {...}}
  ],
  
  "current_step": 2,
  "total_steps": 5,
  
  "c_code": {
    "structure_definition": "struct LinkedListNode { int value; struct LinkedListNode *next; };",
    "active_line": 6,
    "code_snippet": "void insert(LinkedList *list, int value) { ... }"
  },
  
  "console_output": "Insertando valor 20\nInserción completada\n",
  
  "history": [
    "insert(10)",
    "insert(20)",
    "push(30)"
  ],
  
  "metadata": {
    "session_id": "abc123",
    "timestamp": "2026-05-18T14:30:00Z",
    "interpretation_mode": true
  }
}
```

### 9.5 Códigos de Error

```json
{
  "success": false,
  "error_code": "INVALID_INPUT",
  "message": "El campo 'value' debe ser un número entero.",
  "timestamp": "2026-05-18T14:30:00Z"
}
```

Códigos de error comunes:
- `INVALID_INPUT`: Entrada no válida
- `STRUCTURE_NOT_FOUND`: Estructura no existe
- `OPERATION_NOT_SUPPORTED`: Operación no soportada
- `SESSION_EXPIRED`: Sesión expirada
- `SERVER_ERROR`: Error interno del servidor

---

## 10. Especificaciones de Seguridad

### 10.1 Autenticación y Autorización
- **Modelo:** Sin autenticación explícita (educativo)
- **Sesión:** Identificadas por cookie `visualstruct_session`
- **Aislamiento:** Cada sesión tiene su propio estado de estructuras

### 10.2 Protección de Cookies
- `HttpOnly`: True (previene acceso desde JavaScript)
- `SameSite`: Lax (defecto) o Strict
- `Secure`: True en HTTPS (producción)
- `Domain`: Sin especificar (current domain)

### 10.3 Validación de Entrada
**Reglas de Validación:**

- **Secuencial/Jerárquico:** valores deben ser enteros
- **Grafos:**
  - vertex, origin, target, start, end: enteros
  - weight: numérico (int/float)
  - directed: booleano
- **Hash:** key y value como strings (máximo 255 caracteres)

**Implementación:**
```python
def _require_int(payload: dict, key: str, label: str) -> int:
    """Validar y retornar entero requerido."""
    value = str(payload.get(key, "")).strip()
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"El campo '{label}' debe ser entero.")
```

### 10.4 Sanitización
- Escapar salida HTML en templates
- No evaluar usuario input como código
- Limitar tamaño de payloads

### 10.5 Protección CSRF
- Sesiones server-side con token implícito
- Validación de referrer en POST

### 10.6 Rate Limiting (Futuro)
- Considerar implementación para producción
- Limitar operaciones por sesión/IP

### 10.7 Logging y Auditoría
- Registrar operaciones críticas
- No loguear datos sensibles
- Rotación de logs

### 10.8 Configuración Segura
**Producción (variables de entorno):**
```
FLASK_SECRET_KEY=<clave-fuerte-64-caracteres>
FLASK_ENV=production
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=Strict
ENABLE_PROXY_FIX=true
SESSION_REDIS_URL=redis://user:pass@host:6379/0
```

---

## 11. Especificaciones de Configuración

### 11.1 Archivo de Configuración (app/config.py)

```python
class Config:
    # Secret key
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    
    # Templates
    TEMPLATES_AUTO_RELOAD = True  # Dev, False en producción
    
    # Proxy
    ENABLE_PROXY_FIX = True
    
    # Session cookies
    SESSION_COOKIE_NAME = "visualstruct_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"  # "Lax" | "Strict" | "None"
    SESSION_COOKIE_SECURE = False  # True en HTTPS
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=240)  # 4 horas
    SESSION_PERMANENT = True
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Session storage
    SESSION_TYPE = "cachelib"  # "cachelib" | "redis"
    SESSION_KEY_PREFIX = "wved:"
    SESSION_CACHE_DIR = ".flask_session"
    SESSION_CACHE_THRESHOLD = 10000
    SESSION_CACHE_MODE = 0o600
    SESSION_REDIS_URL = None  # "redis://localhost:6379/0"
    
    # Application
    SESSION_MAX_HISTORY = 300  # Máximo histórico por sesión
```

### 11.2 Variables de Entorno

| Variable | Valor Defecto | Descripción |
|---|---|---|
| `FLASK_SECRET_KEY` | dev-secret-key-change-me | Clave secreta (cambiar en producción) |
| `FLASK_ENV` | development | development \| production |
| `FLASK_HOST` | 127.0.0.1 | Host de escucha |
| `FLASK_PORT` | 5050 | Puerto de escucha |
| `TEMPLATES_AUTO_RELOAD` | True | Recargar templates en cambio |
| `ENABLE_PROXY_FIX` | True | Aplicar ProxyFix |
| `SESSION_COOKIE_NAME` | visualstruct_session | Nombre de cookie |
| `SESSION_COOKIE_SECURE` | false | Requiere HTTPS |
| `SESSION_COOKIE_SAMESITE` | Lax | Lax \| Strict \| None |
| `SESSION_LIFETIME_MINUTES` | 240 | Duración de sesión en minutos |
| `SESSION_TYPE` | cachelib | cachelib \| redis |
| `SESSION_CACHE_DIR` | .flask_session | Directorio de caché |
| `SESSION_CACHE_THRESHOLD` | 10000 | Máximo sesiones en caché |
| `SESSION_REDIS_URL` | (none) | URL de Redis (si SESSION_TYPE=redis) |
| `SESSION_MAX_HISTORY` | 300 | Máximo operaciones en historial |

### 11.3 Perfiles de Configuración

**Desarrollo:**
```powershell
$env:FLASK_ENV = "development"
$env:TEMPLATES_AUTO_RELOAD = "true"
$env:SESSION_TYPE = "cachelib"
```

**Producción:**
```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=<clave-fuerte>
export SESSION_COOKIE_SECURE=true
export SESSION_COOKIE_SAMESITE=Strict
export SESSION_TYPE=redis
export SESSION_REDIS_URL=redis://user:pass@host:6379/0
export ENABLE_PROXY_FIX=true
```

---

## 12. Especificaciones de Gestión de Sesiones

### 12.1 Ciclo de Vida de Sesión

1. **Creación:** Primer GET a `/sequential/`, `/hierarchical/`, etc.
2. **Cookie:** Server retorna `Set-Cookie: visualstruct_session=...`
3. **Almacenamiento:** Estado en backend (cachelib/Redis)
4. **Recuperación:** Cada solicitud incluye cookie en header
5. **Renovación:** Se renueva duración si `SESSION_REFRESH_EACH_REQUEST=True`
6. **Expiración:** Después de `SESSION_LIFETIME_MINUTES` de inactividad
7. **Limpieza:** Automática por garbage collector

### 12.2 Contenido de Sesión

```python
session = {
    'session_id': 'abc123...',
    'structures': {
        'sequential_0': {
            'type': 'stack',
            'state': [1, 2, 3],  # Datos internos
            'adapters': {...}
        },
        'hierarchical_0': {
            'type': 'abb',
            'state': {...}
        }
    },
    'history': [
        {'operation': 'push(10)', 'timestamp': '...'},
        {'operation': 'push(20)', 'timestamp': '...'}
    ],
    'created_at': '2026-05-18T10:00:00Z',
    'last_accessed': '2026-05-18T14:30:00Z'
}
```

### 12.3 Backend de Almacenamiento

#### 12.3.1 Cachelib (Filesystem)
- Localización: `.flask_session/`
- Archivo por sesión
- Máximo 10,000 sesiones
- Velocidad: ~1-5ms por operación
- Persistencia: Se pierde si se limpia directorio

#### 12.3.2 Redis
- Conexión: `redis://host:6379/0`
- TTL automático: basado en `PERMANENT_SESSION_LIFETIME`
- Velocidad: ~1-2ms por operación
- Persistencia: RDB/AOF según config Redis
- Escalabilidad: Soporta múltiples instancias

### 12.4 Políticas de Limpieza

- **Automática:** Garbage collector de Flask
- **Manual:** Limpiar `.flask_session/` en desarrollo
- **TTL:** Expiración automática en Redis

---

## 13. Especificaciones de Base de Datos

### 13.1 Almacenamiento de Datos

**No se utiliza base de datos SQL tradicional.**

Datos almacenados:
- **Sesiones:** En cachelib (filesystem) o Redis
- **Estructuras:** En memoria durante sesión activa
- **Configuración:** Variables de entorno y archivo `config.py`
- **Código C:** Archivos estáticos en `docs/tads_C/`

### 13.2 Persistencia

- Sesiones se pierden al reiniciar servidor (cachelib)
- Redis permite persistencia con RDB/AOF
- No se guardan históricos permanentes entre sesiones

### 13.3 Escalabilidad de Almacenamiento

- **Caché filesystem:** Máximo ~100GB con 10,000 sesiones
- **Redis:** Depende de memoria disponible (típicamente 500MB-10GB)
- Ambos soportan limpieza de sesiones antiguas automáticamente

---

## 14. Métricas de Calidad

### 14.1 Cobertura de Código

| Componente | Cobertura | Estado |
|---|---|---|
| `app/__init__.py` | 100% | ✅ Óptimo |
| `app/config.py` | 98% | ✅ Muy bueno |
| `app/routes/main_routes.py` | 100% | ✅ Óptimo |
| `app/adapters/base_adapter.py` | 95% | ✅ Muy bueno |
| `app/services/structure_service.py` | 100% | ✅ Óptimo |
| `app/domain/sequential/` | 92% | ✅ Muy bueno |
| `app/domain/hierarchical/` | 88% | ✅ Bueno |
| `app/domain/graph/` | 85% | ✅ Aceptable |
| `app/domain/hash/` | 87% | ✅ Bueno |
| **Global (`app/`)** | **85%** | ✅ Aceptable |

**Meta:** Mantener cobertura ≥ 85%

### 14.2 Suite de Pruebas

- **Total de casos:** 274
- **Exitosos:** 274 (100%)
- **Fallidos:** 0
- **Omitidos:** 0

**Tipos de pruebas:**
- Unitarias: 180 casos (65%)
- Integración: 70 casos (26%)
- E2E (Playwright): 24 casos (9%)

### 14.3 Criterios de Éxito

| Métrica | Criterio | Estado Actual |
|---|---|---|
| Cobertura | ≥ 85% | 85% ✅ |
| Pruebas | 274 casos | 274 ✅ |
| Documentación | Completa | Sí ✅ |
| Rendimiento | < 200ms por operación | ~50ms ✅ |
| Disponibilidad | 99% uptime | En desarrollo |

### 14.4 Ejecución de Pruebas

```bash
# Suite completa
pytest -q

# Con cobertura
pytest --cov=app --cov-report=term-missing --cov-report=html

# Solo unitarias
pytest -k "not e2e"

# Verbose
pytest -v

# Específico
pytest tests/test_adapters.py::TestStackAdapter
```

---

## 15. Comportamiento de Ejecución e Interpretación

### 15.1 Modo de Interpretación Didáctica Obligatoria

**Principio:** La aplicación debe actuar como un **intérprete gráfico de código C**, no como una reproducción lineal de líneas.

### 15.2 Reglas de Control de Flujo

- Respetar IF/ELSE: solo animar rama tomada
- Respetar bucles (WHILE, FOR): iterar correctamente
- Respetar SWITCH: solo ejecutar case seleccionado
- Mostrar retornos tempranos
- No ejecutar código inalcanzable

### 15.3 Fases de Operación Mutante

Toda operación que modifique estructura debe mostrar:

1. **Estado Inicial**
   - Estructura completa antes de cambio
   - Valores actuales de todos los nodos

2. **Creación de Temporal**
   - Si existe variable temporal (ej: `aux`), mostrarla separada
   - Indicar con etiqueta `Temporal: aux`
   - En diferente área visual (derecha/abajo de estructura)

3. **Asignaciones Intermedias**
   - Mostrar cada asignación de puntero/valor como paso
   - Línea activa de código resaltada
   - Snapshot del estado después de cada asignación

4. **Reasignación a Principal**
   - Paso crítico donde estructura temporal se une a principal
   - Ejemplo: `*p = aux` incorpora temporal
   - Visual: elemento temporal se mueve a su posición final

5. **Estado Final Confirmado**
   - Estructura limpia, sin temporales
   - Valores finales correctos
   - Resaltado del elemento recién modificado

### 15.4 Sincronización de Código C

- Cada paso visual corresponde a línea específica de código C
- Línea activa siempre resaltada en editor de código
- Cuando se avanza visual paso: código C avanza línea
- Cuando se retrocede visual paso: código C retrocede línea
- Scroll automático del código C si es necesario

### 15.5 Salida de Consola (printf)

- Mostrar solo printf() ejecutados en rama actual
- Ejemplo: si rama A imprime "Inserción" pero se ejecuta rama B que imprime "Duplicado", mostrar solo "Duplicado"
- Acumular salida conforme avanzan pasos
- Limpiar al reiniciar estructura

### 15.6 Historial como main()

Mostrar operaciones en formato consistente:

```c
int main() {
    // Operación 1
    push(10);  // Paso 1-5
    
    // Operación 2
    push(20);  // Paso 6-10
    
    // Operación 3
    pop();     // Paso 11-15
    
    return 0;
}
```

### 15.7 Equivalencia de Modo Rápido vs Interpretado

**Modo Interpretado:** Paso a paso completamente detallado
**Modo Rápido:** Solo resultado final sin pasos intermedios

**Regla:** El resultado visual final del modo rápido debe ser idéntico al último paso del modo interpretado.

Ejemplo (Grafo):
- Interpretado: Muestra cada arista explorada en BFS
- Rápido: Muestra al final todas las aristas exploradas
- Resultado: Idéntico resaltado de aristas

### 15.8 Ciclo de Interpretación

```
1. Usuario hace clic en "Ejecutar"
2. Se solicita al servidor: POST /sequential/1/operate
3. Servidor:
   a. Parsea entrada, valida
   b. Obtiene adapter de estructura
   c. Ejecuta adapter.execute(operation, payload)
   d. Recopila execution_trace:
      - trace[0]: línea 1 de C, estado inicial
      - trace[1]: línea 3 de C, estado después
      - trace[2]: línea 5 de C, estado después
      - ... (n pasos)
   e. Retorna JSON con trace completo
4. Cliente:
   a. Recibe JSON
   b. Inicializa índice en paso 0
   c. Renderiza visual del paso 0
   d. Resalta código línea del paso 0
5. Usuario hace clic en "Siguiente paso":
   a. Cliente incrementa índice
   b. Anima transición de paso[i-1] → paso[i]
   c. Resalta nueva línea de código
   d. Actualiza salida de consola
   e. Muestra acción actual
6. Repetir hasta paso final
7. Usuario hace clic en "Reiniciar":
   a. POST /sequential/1/reset
   b. Limpia estado servidor
   c. Cliente reinicia UI
```

---

## 16. Reglas de Validación de Entrada

### 16.1 Validación General

**Todas las entradas deben:**
1. Verificar presencia (no null/vacío)
2. Verificar tipo (string convertible a tipo esperado)
3. Verificar rango (si aplica)
4. Retornar mensaje de error didáctico en español si falla

### 16.2 Validación por Tipo de Estructura

#### Secuencial/Jerárquico
- `value`: Requerido, debe ser entero
- `parent`: Requerido para algunas operaciones, debe ser entero
- `child`: Requerido para algunas operaciones, debe ser entero
- `position`: Opcional, debe ser entero ≥ 0

Ejemplo de error:
```
Campo "value" debe ser un número entero. Ingresado: "abc"
```

#### Grafos
- `vertex`: Entero > 0
- `origin`, `target`: Enteros > 0
- `start`, `end`: Enteros > 0
- `weight`: Numérico (int/float), puede ser negativo
- `directed`: Booleano (true/false, 1/0, si/no)

Ejemplo de error:
```
El peso debe ser un número. Ingresado: "abc"
```

#### Hash
- `key`: String, máximo 255 caracteres, requerido
- `value`: String, máximo 255 caracteres, requerido

Ejemplo de error:
```
La clave no puede estar vacía.
```

### 16.3 Validación de Operación

- Operación debe existir en lista de soportadas
- Estructura debe existir (no null)
- Estado de estructura debe ser válido para operación
  - No se puede desapillar de pila vacía → error amigable

### 16.4 Validación de Sesión

- Sesión debe existir o crearse
- Cookie de sesión debe ser válida
- Si sesión expirada → crear nueva

---

## 17. Flujos de Casos de Uso

### 17.1 Caso de Uso: Insertar en Pila

**Actor:** Estudiante  
**Precondición:** Sesión activa, módulo secuencial abierto

1. Usuario selecciona estructura "Pila"
2. Sistema carga interfaz de Pila
3. Usuario elige operación "push"
4. Sistema muestra input "Valor"
5. Usuario ingresa "10"
6. Usuario marca checkbox "Interpretar paso a paso"
7. Usuario presiona "Ejecutar"
8. Sistema:
   - Valida entrada (10 es entero ✓)
   - Obtiene StackAdapter
   - Ejecuta adapter.execute("push", {"value": 10})
   - Recopila traza de 3 pasos
   - Retorna JSON
9. UI:
   - Carga paso 0: estado inicial (pila vacía)
   - Resalta línea 1 de código C
   - Muestra "Creando nodo..."
10. Usuario presiona "Siguiente paso"
11. UI:
    - Anima transición a paso 1
    - Resalta línea 3 de código C
    - Muestra "Asignando valor..."
    - Visualiza nodo nuevo con valor 10
12. Usuario presiona "Siguiente paso"
13. UI:
    - Anima transición a paso 2 (final)
    - Resalta línea 5 de código C
    - Muestra "Insertando en pila"
    - Muestra nodo en pila visualmente
14. Historia se actualiza: `push(10)`
15. Usuario presiona "Reiniciar"
16. Sistema limpia pila, UI vuelve a estado inicial

### 17.2 Caso de Uso: Buscar en ABB

**Actor:** Estudiante  
**Precondición:** ABB con elementos ya insertados

1. Usuario selecciona estructura "ABB"
2. Usuario elige operación "búsqueda"
3. Usuario ingresa valor "15"
4. Usuario marca "Interpretar paso a paso"
5. Usuario presiona "Ejecutar"
6. Sistema:
   - Valida entrada (15 es entero ✓)
   - Ejecuta búsqueda en árbol
   - Recopila traza: cada iteración de búsqueda
   - Si encontrado: último paso resalta el nodo
   - Si no encontrado: último paso muestra mensaje
7. UI:
   - Paso 0: muestra árbol completo
   - Paso 1: resalta nodo raíz, explica comparación
   - Paso 2: resalta nodo hijo izq/der según comparación
   - ... (hasta encontrar o descartar)
   - Código C sincronizado en cada paso

### 17.3 Caso de Uso: Recorrido DFS en Grafo

**Actor:** Estudiante  
**Precondición:** Grafo construido con aristas

1. Usuario en módulo Grafos, Paso 3: Ejecutar algoritmo
2. Usuario selecciona "Recorrido DFS"
3. Usuario elige vértice de inicio "1"
4. Usuario marca "Interpretar paso a paso"
5. Usuario presiona "Ejecutar"
6. Sistema:
   - Valida entrada (1 es vértice válido ✓)
   - Ejecuta DFS desde 1
   - Recopila traza: cada visita de nodo
   - Orden final: [1, 3, 4, 2] (ej)
7. UI:
   - Paso 0: todos los nodos en color normal
   - Paso 1: nodo 1 resaltado, código en línea de inicialización
   - Paso 2: nodo 1 visitado (color visitado), nodo 3 procesando (color activo)
   - Paso 3: nodo 3 visitado, nodo 4 procesando
   - ... (continúa hasta todos visitados)
   - Acción actual alterna entre "Evaluando condición" y "Aplicando cambio"
8. Usuario presiona "Reproducir": animación automática a velocidad configurable
9. Usuario presiona "Anterior paso": retrocede un paso
10. Resultado: Orden de visitación en historial

### 17.4 Caso de Uso: Buscar en Tabla Hash

**Actor:** Estudiante  
**Precondición:** Tabla hash con elementos

1. Usuario selecciona estructura "Tabla Hash"
2. Usuario elige operación "búsqueda"
3. Usuario ingresa clave "nombre"
4. Usuario presiona "Ejecutar"
5. Sistema:
   - Valida entrada (string ✓)
   - Ejecuta búsqueda en tabla
   - Hash genera índice
   - Busca en cadena de colisiones si es necesario
   - Recopila traza
6. UI:
   - Visualiza tabla completa
   - Resalta índice calculado del hash
   - Si hay colisión, resalta cadena recorrida
   - Resultado: encontrado con valor o no encontrado
7. Historia: `search("nombre") → valor`

---

## 18. Endpoints Principales

### Resumen de Endpoints

| Método | Ruta | Descripción | Requiere Sesión |
|---|---|---|---|
| GET | `/` | Página inicio | No |
| GET | `/healthz` | Health check | No |
| GET | `/assets/<path:filename>` | Assets estáticos | No |
| GET | `/sequential/` | Módulo secuencial | Sí |
| POST | `/sequential/<id>/operate` | Ejecutar operación secuencial | Sí |
| POST | `/sequential/<id>/reset` | Reiniciar secuencial | Sí |
| GET | `/hierarchical/` | Módulo jerárquico | Sí |
| POST | `/hierarchical/<id>/operate` | Ejecutar operación jerárquica | Sí |
| POST | `/hierarchical/<id>/reset` | Reiniciar jerárquico | Sí |
| GET | `/graph/` | Módulo grafos | Sí |
| GET | `/graph/<id>/<phase>` | Obtener fase de grafo | Sí |
| POST | `/graph/<id>/operate` | Ejecutar operación en grafo | Sí |
| POST | `/graph/<id>/reset` | Reiniciar grafo | Sí |
| GET | `/hash/` | Módulo hash | Sí |
| POST | `/hash/<id>/operate` | Ejecutar operación hash | Sí |
| POST | `/hash/<id>/reset` | Reiniciar hash | Sí |
| GET | `/help/<module>` | Ayuda de módulo | No |
| GET | `/help/<module>/<structure>` | Ayuda de estructura | No |

---

## Conclusión

Este documento especifica de forma completa:
- **Funcionalidad:** 18 requisitos funcionales principales
- **Calidad:** 85% cobertura, 274 pruebas exitosas
- **Arquitectura:** 5 capas lógicas, 13 adapters
- **API:** 18 endpoints REST
- **Seguridad:** Validación completa, sesiones seguras
- **Usabilidad:** Interfaz didáctica, mensajes en español
- **Mantenibilidad:** Documentada, modular, testeable

**Base sólida para SDD:** Este documento proporciona todas las especificaciones necesarias para desarrollar y mantener la aplicación VisualEstructuras de datos de forma consistente y profesional.

---

**Firma de Aprobación:**  
Versión: 1.0  
Fecha: 18 de mayo de 2026  
Estado: Listo para SDD
