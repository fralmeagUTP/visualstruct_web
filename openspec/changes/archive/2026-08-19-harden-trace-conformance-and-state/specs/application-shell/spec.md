# Delta: application-shell

## MODIFIED Requirements

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

## ADDED Requirements

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
