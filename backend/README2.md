# Test Automation API

Este proyecto contiene la estructura básica de un backend en Python utilizando FastAPI y SQLAlchemy. Incluye modelos para usuarios y pruebas, autenticación mediante JWT y rutas CRUD protegidas. Es un punto de partida para ampliar con funcionalidades de automatización de pruebas.

## Requisitos

- Python 3.11
- Postgres

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

Configura la variable `DATABASE_URL` según tu entorno y ejecuta la aplicación desde la raíz del repositorio:

```bash
uvicorn backend.app.main:app --reload
```

Si prefieres iniciar el servidor dentro de la carpeta `backend`, usa la ruta relativa del paquete:

```bash
cd backend
uvicorn app.main:app --reload
```

## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.

## Roles y permisos

Al iniciar la aplicación se crean automáticamente los roles:

- Administrador
- Arquitecto de Automatización
- Automation Engineer
- Analista de Pruebas con skill de automatización
- Automatizador de Pruebas
- Gerente de servicios

También se genera el usuario inicial `admin` con la contraseña `admin` perteneciente al rol **Administrador**.
Además, se crean tres usuarios predeterminados:

- `architect` con rol **Arquitecto de Automatización** (contraseña `architect`)
- `service_manager` con rol **Gerente de servicios** (contraseña `service_manager`)
- `test_automator` con rol **Automatizador de Pruebas** (contraseña `test_automator`)

Ahora cada rol puede tener permisos asociados a las páginas del frontend. Usa los siguientes endpoints para administrarlos:

- `GET /roles/{id}/permissions` listar permisos de un rol
- `POST /roles/{id}/permissions` agregar un permiso enviando `{ "page": "nombre" }`
- `DELETE /roles/{id}/permissions/{page}` eliminar un permiso

## Clientes y proyectos

Los clientes pueden ser creados y actualizados por usuarios con rol **Administrador** o **Gerente de servicios**, mientras que la eliminación sigue reservada al **Administrador**. El **Gerente de servicios** puede crear proyectos para cada cliente y asignar analistas. Un cliente puede tener varios proyectos y ambos pueden inactivarse. Los analistas se asignan a los proyectos y solamente los analistas asignados (o los usuarios Administrador) pueden consultarlos. Cada proyecto cuenta con un **objetivo** y al asignar un analista se deben indicar la cantidad de **scripts por día** esperados y los **tipos de prueba** (funcional web, APIs, móviles, performance).
Los roles **Analista de Pruebas** y **Automatizador de Pruebas** pueden consultar los clientes que tengan asignados y ver la dedicación indicada para cada uno.


Endpoints principales:

- `POST /clients/` crear cliente
- `PUT /clients/{id}` actualizar cliente
- `DELETE /clients/{id}` inactivar cliente
- `POST /clients/{id}/analysts/{user_id}` asignar analista a cliente (parámetro `dedication` opcional)
- `DELETE /clients/{id}/analysts/{user_id}` quitar analista de cliente
- `GET /clients/` listar clientes (para analistas solo los asignados con dedicación)
- `POST /projects/` crear proyecto vinculado a un cliente
- `PUT /projects/{id}` actualizar proyecto
- `DELETE /projects/{id}` inactivar proyecto
- `POST /projects/{id}/analysts/{user_id}` asignar analista (parámetros `scripts_per_day` y `test_types`)
- `DELETE /projects/{id}/analysts/{user_id}` quitar analista
- `GET /projects/` listar proyectos asignados al usuario

### Planes de prueba

Los planes de prueba siguen las buenas prácticas de ISTQB y Business Centric Testing. El campo `nombre` es obligatorio y debe tener al menos 5 caracteres.
Cada plan también incluye:

- `objetivo`
- `alcance`
- `criterios_entrada` y `criterios_salida`
- `estrategia`
- `responsables`
- `fecha_inicio` y `fecha_fin`
- Se valida que `fecha_inicio` sea anterior o igual a `fecha_fin`
- `historias_bdd` para la trazabilidad a BDD

Endpoints:

- `POST /testplans/` crear plan de prueba
- `GET /testplans/` listar planes de prueba
- `GET /testplans/{id}` obtener un plan de prueba
- `PUT /testplans/{id}` actualizar plan de prueba
- `DELETE /testplans/{id}` eliminar plan de prueba

### Páginas y localizadores

Se implementa la gestión de páginas siguiendo el patrón Screenplay. Cada página puede contener múltiples elementos (botones, campos de entrada, etc.). Para cada elemento se registran:

- `nombre`
- `tipo`
- `estrategia` de localización (`xpath`, `css`, `id`)
- `valor` del localizador
- `descripcion` de uso

Los elementos son únicos por página y pueden asociarse a casos de prueba para favorecer su reutilización en distintos flujos.

Endpoints principales:

- `POST /pages/` crear página
- `GET /pages/` listar páginas
- `PUT /pages/{id}` actualizar página
- `DELETE /pages/{id}` eliminar página
- `POST /elements/` crear elemento
- `GET /elements/` listar elementos
- `PUT /elements/{id}` actualizar elemento
- `DELETE /elements/{id}` eliminar elemento
- `POST /elements/{id}/tests/{test_id}` asociar elemento a caso de prueba
- `DELETE /elements/{id}/tests/{test_id}` desasociar elemento del caso de prueba

### Acciones de automatización

Las acciones permiten definir operaciones reutilizables como "dar click" o "escribir texto".
Cada acción incluye:

- `nombre`
- `tipo`
- `codigo` Python/JS que se ejecutará
- `argumentos` necesarios (por ejemplo: localizador, texto, tiempo)

El código se valida para evitar instrucciones peligrosas. Las acciones pueden asociarse a `TestCase` para su ejecución parametrizada.

Endpoints principales:

- `POST /actions/` crear acción
- `GET /actions/` listar acciones
- `GET /actions/{id}` obtener acción
- `PUT /actions/{id}` actualizar acción
- `DELETE /actions/{id}` eliminar acción
- `POST /actions/{id}/tests/{test_id}` asociar acción a un caso de prueba
- `DELETE /actions/{id}/tests/{test_id}` desasociar acción del caso de prueba

### Asignación de acciones a objetos

Permite vincular una acción con un elemento de página en un `TestCase` e indicar los parámetros concretos a usar. Se valida que los parámetros requeridos por la acción estén presentes.

Endpoints principales:

- `POST /assignments/` crear asignación
- `GET /assignments/` listar asignaciones
- `GET /assignments/{id}` obtener una asignación
- `PUT /assignments/{id}` actualizar asignación
- `DELETE /assignments/{id}` eliminar asignación

### Agentes de ejecución

Los agentes representan máquinas o dispositivos en los que se ejecutan las pruebas. Deben registrar:

- `alias`
- `hostname` único en toda la plataforma
- `os` (Windows, Linux, Mac, Android, iOS)
- `categoria` opcional `granja móvil` para dispositivos Android/iOS

Al registrarse en `/agent/register` el backend genera una API key que el agente debe usar en los demás endpoints de comunicación.

Endpoints principales:

- `POST /agents/` crear agente
- `GET /agents/` listar agentes
- `GET /agents/{id}` obtener agente
- `PUT /agents/{id}` actualizar agente
- `DELETE /agents/{id}` eliminar agente
- `POST /agent/register` registro automático de un agente y obtención de API key
- `POST /agent/heartbeat` notificación de vida usando la API key
- `GET /agent/pending` consulta de la ejecución pendiente con API key
- `POST /agent/status` actualización de estado y logs
- `POST /agent/result` envío del archivo de resultados

Adicionalmente, existe un canal WebSocket en `/ws/agent` utilizado por los agentes
para registrarse con sus capacidades y enviar heartbeats de manera continua.
El backend realiza ping cada 30 segundos y asigna ejecuciones de la cola a
los agentes conectados.

### Planes de ejecución

Un plan de ejecución define qué caso de prueba se ejecutará y en qué agente.
Se valida que el `TestCase` y el agente existan antes de crearlo.

Endpoints principales:

- `POST /executionplans/` crear plan de ejecución
- `GET /executionplans/` listar planes con filtros opcionales `agent_id`, `test_id` o `nombre`
- `GET /executionplans/{id}` obtener plan
- `PUT /executionplans/{id}` actualizar plan
- `DELETE /executionplans/{id}` eliminar plan
- `POST /executionplans/{id}/run` disparar la ejecución y registrar el estado inicial. Si el agente ya tiene una ejecución pendiente se rechaza la petición.
- `GET /agents/{hostname}/pending` un agente autenticado consulta su próxima ejecución pendiente y recibe el plan, caso de prueba, elementos y acciones con parámetros

Además, el helper `prepare_execution_payload(test_id)` genera el script compilado, datos de contexto y configuración necesarios que el backend envía al agente.

### Métricas

El rol **Arquitecto de Automatización** puede consultar un resumen general de clientes, proyectos, analistas asignados y flujos de pruebas.

Endpoints principales:

- `GET /metrics/overview` obtener el listado de clientes con sus proyectos y analistas junto con todos los flujos registrados

## Colección Postman

Para facilitar las pruebas manuales o de integración se incluye el script
`generate_postman.py` ubicado en la raíz del repositorio. Al ejecutarlo se toma
el esquema OpenAPI de la aplicación y se genera automáticamente una colección
compatible con Postman.

```bash
python generate_postman.py
```

Se crearán los archivos `postman/collection.json` y `postman/environment.json`
que puedes importar directamente en Postman. La colección contiene ejemplos de
cada endpoint y variables de entorno como `base_url` y `token` para que puedas
ejecutar las peticiones rápidamente.

## Integración con Jira

Existe un cliente básico para Jira que permite crear issues, transicionar su estado y lanzar pipelines externos. Los endpoints disponibles son:

- `POST /integrations/jira/issue`
- `POST /integrations/jira/issues/{issue_key}/status`
- `POST /integrations/jira/pipeline`

Configura las variables `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` y `JIRA_PROJECT_KEY` antes de usar estas llamadas.

