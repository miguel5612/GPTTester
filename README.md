# GPTTester Repository

El backend desarrollado en FastAPI se encuentra dentro de la carpeta `backend`.

Para conocer los detalles de instalación y uso del backend revisa `backend/README.md`.

La carpeta `postman` se genera automáticamente ejecutando `python generate_postman.py` y
contiene una colección lista para importar en Postman y probar todos los endpoints.
De forma similar puedes generar un script de carga para K6 ejecutando
`python generate_k6.py`. Esto crea `k6/script.js` a partir de los datos
definidos en `tests/pools/` y la API de FastAPI, permitiendo correr
escenarios *baseline*, *stress*, *spike* y *soak*. El script también puede
descargarse desde la sección **Performance** en la interfaz web.
- `historias_bdd` para la trazabilidad a BDD
- Marketplace de componentes disponible en `/marketplace/components/`
- 
## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.

Para conocer el marco de governance consulta [GOVERNANCE.md](GOVERNANCE.md).

Los administradores pueden revisar los eventos registrados consultando `/audit-events` y gestionar secretos en `/secrets/`.

## Integraciones externas

La API incluye endpoints de vista previa para conectarse con Jira u otros servicios que acepten peticiones HTTP. Con una cuenta gratuita puedes:

- Crear incidencias con `POST /integrations/jira/issue`.
- Cambiar su estado mediante `POST /integrations/jira/issues/{issue_key}/status`.
- Lanzar pipelines externos desde `POST /integrations/jira/pipeline`.

Configura las variables `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` y `JIRA_PROJECT_KEY` para habilitar estas integraciones.

## Wiki colaborativa

Este repositorio incluye un directorio [`wiki`](wiki/) que funciona como espacio de documentación colaborativa. Cualquier rol puede proponer mejoras o nuevas herramientas para el agente registrando sus ideas en [`wiki/ideas.md`](wiki/ideas.md).

