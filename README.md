# GPTTester Repository

Este repositorio contiene distintos componentes relacionados con automatización de pruebas.
El backend desarrollado en FastAPI se encuentra dentro de la carpeta `backend`.

Para conocer los detalles de instalación y uso del backend revisa `backend/README.md`.
- `historias_bdd` para la trazabilidad a BDD

Endpoints:

- `POST /testplans/` crear plan de prueba
- `GET /testplans/` listar planes de prueba
- `GET /testplans/{id}` obtener un plan de prueba
- `PUT /testplans/{id}` actualizar plan de prueba
- `DELETE /testplans/{id}` eliminar plan de prueba

## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.
