# application-shell Specification

## Purpose

Define el núcleo de la aplicación Flask: factory de aplicación, configuración por
entorno, registro de blueprints, página de inicio, health check y servido de assets.
Es la base sobre la que se montan todos los módulos de estructuras.
## Requirements
### Requirement: Application Factory
El sistema MUST exponer una función `create_app(config_class)` que construya y
configure la aplicación Flask con templates y estáticos servidos desde la raíz del
proyecto (`templates/` y `static/` con `static_url_path="/static"`), cargue la
configuración desde la clase `Config`, configure el backend de sesión y los headers
de proxy, y registre los blueprints de todos los módulos.

#### Scenario: arranque con configuración por defecto
- **GIVEN** no se define ninguna variable de entorno
- **WHEN** se invoca `create_app()`
- **THEN** la aplicación se crea con `Config` por defecto, sesiones `cachelib` en
  `.flask_session/` y todos los blueprints registrados (`main`, `sequential`,
  `hierarchical`, `graph`, `hash`, `sorting`, `sorting_api`, `help`)

#### Scenario: factory usada por tests
- **GIVEN** el fixture `app` de `tests/conftest.py`
- **WHEN** invoca `create_app()` y actualiza `TESTING=True` y `SECRET_KEY`
- **THEN** la app resultante funciona con `test_client()` sin efectos colaterales

### Requirement: Configuración por variables de entorno
El sistema MUST leer su configuración de variables de entorno e incluir `APP_ENV` con valores
`development`, `testing` o `production`; `FLASK_SECRET_KEY`; `FLASK_HOST` (default `127.0.0.1`);
`FLASK_PORT` (default `5050`); `SESSION_TYPE`; `SESSION_REDIS_URL`;
`SESSION_COOKIE_SECURE`; `SESSION_COOKIE_SAMESITE` (default `Lax`);
`SESSION_LIFETIME_MINUTES` (default `240`); `SESSION_MAX_HISTORY` (default `300`);
`ENABLE_PROXY_FIX`; cantidad de proxies confiables; e intervalo de checkpoints. Las variables
booleanas DEBEN parsearse aceptando `1/true/yes/on`.

En `production`, la aplicación DEBE rechazar el arranque cuando la clave secreta falte o conserve
el valor de desarrollo, cuando la cookie segura esté desactivada sin override explícito, o cuando
ProxyFix esté habilitado sin una cantidad explícita de proxies confiables.

#### Scenario: configuración cómoda de desarrollo
- **GIVEN** `APP_ENV=development` y sin clave explícita
- **WHEN** se crea la aplicación
- **THEN** se permite la clave de desarrollo y se registra una advertencia visible

#### Scenario: clave secreta por defecto en desarrollo
- **GIVEN** `FLASK_SECRET_KEY` no está definida
- **WHEN** se crea la aplicación
- **THEN** `SECRET_KEY` usa el valor de desarrollo `"dev-secret-key-change-me"`

#### Scenario: secreto inseguro en producción
- **GIVEN** `APP_ENV=production` y `FLASK_SECRET_KEY=dev-secret-key-change-me`
- **WHEN** se crea la aplicación
- **THEN** el arranque falla con un mensaje accionable sin imprimir el secreto

#### Scenario: cookie insegura en producción
- **GIVEN** `APP_ENV=production` y `SESSION_COOKIE_SECURE=false` sin override
- **WHEN** se crea la aplicación
- **THEN** el arranque falla e indica la variable que debe corregirse

#### Scenario: booleano de entorno parseado correctamente
- **GIVEN** `ENABLE_PROXY_FIX=false`
- **WHEN** se crea la aplicación
- **THEN** `app.config["ENABLE_PROXY_FIX"]` es `False` y no se aplica `ProxyFix`

### Requirement: Soporte de proxy reverso
El sistema MUST aplicar `ProxyFix` únicamente cuando `ENABLE_PROXY_FIX` sea verdadero y la
cantidad de proxies confiables esté configurada explícitamente. Los parámetros `x_for`,
`x_proto`, `x_host` y `x_port` DEBEN derivarse de esa configuración y NO DEBEN confiar por
defecto en cabeceras reenviadas en producción.

#### Scenario: proxy confiable configurado
- **GIVEN** `APP_ENV=production`, `ENABLE_PROXY_FIX=true` y un proxy confiable
- **WHEN** la app recibe una request a través de ese proxy
- **THEN** Flask resuelve esquema, host, puerto e IP usando exactamente el salto configurado

#### Scenario: despliegue detrás de proxy
- **GIVEN** `ENABLE_PROXY_FIX=true` y una cantidad explícita de proxies confiables
- **WHEN** la app recibe una request con headers `X-Forwarded-*`
- **THEN** Flask resuelve esquema, host y puerto según los headers del proxy

#### Scenario: proxy habilitado sin confianza explícita
- **GIVEN** `APP_ENV=production` y `ENABLE_PROXY_FIX=true` sin cantidad de proxies
- **WHEN** se crea la aplicación
- **THEN** el arranque falla antes de servir solicitudes

### Requirement: Página de inicio
El sistema MUST responder `GET /` renderizando `index.html` con el menú de módulos
disponibles.

#### Scenario: carga del inicio
- **WHEN** un cliente hace `GET /`
- **THEN** responde `200` con el HTML de la página principal

### Requirement: Health check
El sistema MUST responder `GET /healthz` con JSON `{"status": "ok"}` y código `200`
para chequeos de despliegue.

#### Scenario: liveness probe
- **WHEN** un cliente hace `GET /healthz`
- **THEN** recibe `200` con cuerpo `{"status": "ok"}`

### Requirement: Servido de assets
El sistema MUST servir los archivos del directorio raíz `assets/` (imágenes de los
módulos y logotipos) bajo la ruta `GET /assets/<path:filename>`.

#### Scenario: descarga de imagen de módulo
- **GIVEN** existe `assets/pila.jpg`
- **WHEN** un cliente hace `GET /assets/pila.jpg`
- **THEN** recibe el archivo con `200`

### Requirement: Entry points de ejecución
El sistema MUST proveer dos entry points: `run.py` para desarrollo local (escucha en
`FLASK_HOST`:`FLASK_PORT`, sin debug ni reloader) y `wsgi.py` exponiendo `app` para
servidores WSGI de producción (waitress sugerido).

#### Scenario: arranque local por defecto
- **WHEN** se ejecuta `python run.py` sin variables de entorno
- **THEN** el servidor escucha en `127.0.0.1:5050`

#### Scenario: despliegue con waitress
- **WHEN** se ejecuta `python -m waitress --host=0.0.0.0 --port=5050 wsgi:app`
- **THEN** la aplicación queda servida vía WSGI en el puerto indicado

### Requirement: Jobs de calidad independientes
La integración continua MUST ejecutar en jobs independientes las pruebas unitarias/integración,
E2E con navegador instalado, conformidad C↔Python y verificación C con sanitizers. La ausencia de
una dependencia de infraestructura DEBE reportarse como error de configuración distinguible de
un fallo funcional.

#### Scenario: navegador E2E ausente
- **GIVEN** un entorno local sin Chromium de Playwright
- **WHEN** se invoca la suite E2E
- **THEN** el comando de preparación documentado permite instalarlo
- **AND** el error no se presenta como regresión funcional del producto

#### Scenario: gate de cobertura crítico
- **GIVEN** un cambio que reduce un motor de dominio crítico por debajo de 85%
- **WHEN** se ejecuta el job unitario
- **THEN** el job falla aunque la cobertura global permanezca sobre 83%

### Requirement: Métricas y logs operativos sin datos sensibles
El sistema MUST registrar duración y cantidad de operaciones de replay, uso o descarte de
checkpoint, estrategia de traza y cantidad de pasos generados. Los logs NO DEBEN incluir cookies,
secretos ni payloads completos de usuario.

#### Scenario: fallback de checkpoint observado
- **GIVEN** un checkpoint incompatible
- **WHEN** el sistema hace fallback a replay completo
- **THEN** registra estructura, motivo no sensible y duración
- **AND** no registra contenido de sesión ni credenciales

