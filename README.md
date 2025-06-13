# GPTTester Repository

El backend desarrollado en FastAPI se encuentra dentro de la carpeta `backend`.

Para conocer los detalles de instalación y uso del backend revisa `backend/README.md`.

La carpeta `postman` se genera automáticamente ejecutando `python generate_postman.py` y
contiene una colección lista para importar en Postman y probar todos los endpoints.
- `historias_bdd` para la trazabilidad a BDD
- 
## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.
