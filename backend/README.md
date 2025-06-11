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
