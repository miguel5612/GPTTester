# Estructura de Pruebas

Este directorio define una arquitectura de pruebas unificada para Web, API,
Mobile y Performance.

## Conceptos Principales

- **Data Objects compartidos**: Modelos en `data_objects.py` reutilizables en
  cualquier canal.
- **Test Data Factory**: `DataFactory` carga pools de datos según el ambiente
  especificado por la variable `TEST_ENV`.
- **Herencia de Casos de Prueba**: `BaseHappyPath` provee un flujo principal que
  se especializa por canal en `test_cases/`.
- **Variables de Contexto Globales**: `load_context()` expone configuración
  común (por ejemplo `BASE_URL`).
La carpeta se divide en `unit`, `integration` y `e2e` para distinguir los niveles de prueba.


Ejecuta las pruebas con:

```bash
pytest tests
```
