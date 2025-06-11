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
