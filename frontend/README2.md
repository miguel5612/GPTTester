# Frontend Angular - Sistema de Automatización de Pruebas

Este es el frontend desarrollado en Angular con TypeScript y Bootstrap para el sistema de automatización de pruebas.

### Estado actual
Por ahora la aplicación solo incluye las pantallas de inicio de sesión, registro y la gestión básica de clientes y actores.

## Características

- **Framework**: Angular 17 con TypeScript
- **Estilos**: Bootstrap 5 + SCSS personalizado
- **Diseño**: Implementa el diseño especificado con colores y animaciones
- **Arquitectura**: Componentes standalone con lazy loading
- **API**: Integración completa con el backend FastAPI

## Colores del Diseño

- **Fondo general**: #E6F0FA y #D9EBFF (gradiente)
- **Panel principal**: #FFFFFF
- **Botón primario**: #3399FF con texto #FFFFFF
- **Títulos**: #1A1A1A y #333333
- **Campos de entrada**: #F9F9F9 con bordes #DDDDDD
- **Texto secundario**: #666666

## Tipografía

- **Fuente principal**: Inter, Roboto, Open Sans, Lato
- **Jerarquía clara** para encabezados, botones y formularios

## Animaciones

- **Fade-in del fondo** al cargar
- **Animación de entrada del panel** (scale + fade)
- **Animaciones secuenciales** para secciones
- **Efectos hover** en botones y elementos interactivos
- **Animaciones de progreso** para flujos
- **Transiciones suaves** en todos los elementos

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── dashboard/          # Dashboard principal con flow builder
│   │   │   ├── login/              # Componente de login
│   │   │   ├── actors/             # Gestión de actores
│   │   │   ├── flow-builder/       # Constructor de flujos
│   │   │   ├── test-plans/         # Planes de prueba
│   │   │   └── execution/          # Centro de ejecución
│   │   ├── services/
│   │   │   └── api.service.ts      # Servicio para comunicación con backend
│   │   ├── models/
│   │   │   └── index.ts            # Interfaces TypeScript
│   │   ├── app.component.ts        # Componente raíz
│   │   └── app.routes.ts           # Configuración de rutas
│   ├── styles.scss                 # Estilos globales con variables CSS
│   └── index.html                  # Página principal
├── angular.json                    # Configuración de Angular
├── package.json                    # Dependencias del proyecto
└── tsconfig.json                   # Configuración de TypeScript
```

## Funcionalidades Implementadas

### Dashboard Principal
- **Gestión de Actores**: Visualización de agentes disponibles
- **Constructor de Flujos**: Interfaz tipo flow builder para crear automatizaciones
- **Progreso Visual**: Barra de progreso con indicadores de pasos
- **Vista Previa**: Simulación de ejecución de flujos
- **Logs y Debug**: Panel de logs con diferentes niveles
- **Acciones Rápidas**: Navegación rápida a otras secciones

### Características del Flow Builder
- **Selección de Tests**: Grid de casos de prueba disponibles
- **Acciones Disponibles**: Lista de acciones que se pueden agregar
- **Constructor Visual**: Interfaz drag-and-drop style para construir flujos
- **Condiciones Dinámicas**: Campos expandibles para agregar condiciones
- **Vista Previa Animada**: Simulación paso a paso de la ejecución
- **Validación en Tiempo Real**: Feedback visual del estado del flujo

### Sistema de Autenticación
- **Login Seguro**: Integración con JWT del backend
- **Gestión de Sesiones**: Manejo automático de tokens
- **Redirección Inteligente**: Navegación basada en estado de autenticación

## Instalación y Ejecución

### Prerrequisitos
- Node.js (versión LTS recomendada)
- npm o yarn
- Angular CLI

### Pasos de Instalación

1. **Navegar al directorio frontend**:
   ```bash
   cd frontend
   ```

2. **Instalar dependencias**:
   ```bash
   npm install
   ```

3. **Ejecutar la aplicación**:
   ```bash
   npx ng serve
   ```

4. **Abrir en el navegador**:
   ```
   http://localhost:4200
   ```

### Credenciales por Defecto
- **Usuario**: admin
- **Contraseña**: admin

## Configuración del Backend

Asegúrate de que el backend FastAPI esté ejecutándose en `http://localhost:8000` antes de usar la aplicación.

## Scripts Disponibles

- `npm start` o `npx ng serve`: Ejecuta el servidor de desarrollo
- `npm run build`: Construye la aplicación para producción
- `npm test`: Ejecuta las pruebas unitarias
- `npm run watch`: Construye en modo watch para desarrollo

## Integración con Backend

La aplicación se conecta automáticamente con el backend FastAPI a través del servicio `ApiService` que maneja:

- **Autenticación**: Login/logout con JWT
- **Gestión de Usuarios**: CRUD de usuarios y roles
- **Gestión de Proyectos**: CRUD de clientes y proyectos
- **Gestión de Tests**: CRUD de casos de prueba
- **Gestión de Actores**: CRUD de agentes de ejecución
- **Planes de Ejecución**: Creación y monitoreo de ejecuciones

## Responsive Design

La aplicación está optimizada para:
- **Desktop**: Experiencia completa con todas las funcionalidades
- **Tablet**: Adaptación de layouts para pantallas medianas
- **Mobile**: Interfaz simplificada para dispositivos móviles

## Próximas Funcionalidades

- Gestión completa de actores
- Editor avanzado de flujos
- Reportes y analytics
- Notificaciones en tiempo real
- Integración con sistemas externos

## Soporte

Para problemas o preguntas sobre el frontend, consulta la documentación del backend o contacta al equipo de desarrollo.
