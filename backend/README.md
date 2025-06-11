# Test Automation API

Este proyecto contiene la estructura b\u00e1sica de un backend en Python utilizando FastAPI y SQLAlchemy. Incluye modelos para usuarios y pruebas, autenticaci\u00f3n mediante JWT y rutas CRUD protegidas. Es un punto de partida para ampliar con funcionalidades de automatizaci\u00f3n de pruebas.

## Requisitos

- Python 3.11
- Postgres

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

Configura la variable `DATABASE_URL` seg\u00fan tu entorno y ejecuta la aplicaci\u00f3n:

```bash
uvicorn backend.app.main:app --reload
```

## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.

## Roles y permisos

Al iniciar la aplicación se crean automáticamente los roles:

- Administrador
- Arquitecto de Automatización
- Automation Engineer
- Analista de Pruebas con skill de automatización

También se genera el usuario inicial `admin` con la contraseña `admin` perteneciente al rol **Administrador**.

Solo los usuarios con rol Administrador pueden administrar roles y asignarlos a otros usuarios mediante los endpoints bajo `/roles/` y `/users/{id}/role`.

## Clientes y proyectos

Los clientes y proyectos pueden gestionarse únicamente por usuarios con rol **Administrador**. Un cliente puede tener varios proyectos y ambos pueden inactivarse. Los analistas se asignan a los proyectos y solamente los analistas asignados (o los usuarios Administrador) pueden consultarlos.

Endpoints principales:

- `POST /clients/` crear cliente
- `PUT /clients/{id}` actualizar cliente
- `DELETE /clients/{id}` inactivar cliente
- `POST /projects/` crear proyecto vinculado a un cliente
- `PUT /projects/{id}` actualizar proyecto
- `DELETE /projects/{id}` inactivar proyecto
- `POST /projects/{id}/analysts/{user_id}` asignar analista
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

Se implementa la gestión de páginas siguiendo el patrón Screenplay. Cada página
puede contener múltiples elementos (botones, campos de entrada, etc.). Para cada
elemento se registran:

- `nombre`
- `tipo`
- `estrategia` de localización (`xpath`, `css`, `id`)
- `valor` del localizador
- `descripcion` de uso

Los elementos son únicos por página y pueden asociarse a casos de prueba para
favorecer su reutilización en distintos flujos.

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

Permite vincular una acción con un elemento de página en un `TestCase` e indicar
los parámetros concretos a usar. Se valida que los parámetros requeridos por la
acción estén presentes.

Endpoints principales:

- `POST /assignments/` crear asignación
- `GET /assignments/` listar asignaciones
- `GET /assignments/{id}` obtener una asignación
- `PUT /assignments/{id}` actualizar asignación
- `DELETE /assignments/{id}` eliminar asignación

### Agentes de ejecuci\u00f3n

Los agentes representan m\u00e1quinas o dispositivos en los que se ejecutan las pruebas. Deben registrar:

- `alias`
- `hostname` \u00fanico en toda la plataforma
- `os` (Windows, Linux, Mac, Android, iOS)
- `categoria` opcional `granja m\u00f3vil` para dispositivos Android/iOS

Endpoints principales:

- `POST /agents/` crear agente
- `GET /agents/` listar agentes
- `GET /agents/{id}` obtener agente
- `PUT /agents/{id}` actualizar agente
- `DELETE /agents/{id}` eliminar agente

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
