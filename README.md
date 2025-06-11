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

## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.
