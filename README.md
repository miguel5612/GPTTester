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
- 
## Autenticación

Regístrate enviando un POST a `/users/` con `username` y `password`. El login se realiza en `/token` utilizando un formulario `application/x-www-form-urlencoded`.
