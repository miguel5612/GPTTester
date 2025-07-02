# Diagrama General de la Base de Datos

A continuación se muestra primero un esquema simplificado para facilitar la comprensión de los distintos dominios:

```mermaid
flowchart TB
    Usuarios["Usuarios y seguridad"] --> Clientes["Clientes y proyectos"]
    Clientes --> Interacciones["Interacciones y validaciones"]
    Interacciones --> Escenarios["Escenarios y datos de prueba"]
```

Para quienes requieran más detalle también se incluye un diagrama UML con todas las tablas relevantes:

```mermaid
classDiagram
    Role <|-- User
    Role <|-- PagePermission
    Role <|-- ApiPermission
    Client <|-- BusinessAgreement
    Client <|-- DigitalAsset
    DigitalAsset <|-- UserInterface
    UserInterface <|-- Element
    Element --> ElementType
    DigitalAsset <|-- Project
    Project <|-- ProjectEmployee
    User <|-- ProjectEmployee
    Client <|-- Actor
    Actor --> Hability
    Interaction <|-- InteractionParameter
    Interaction <|-- TaskHaveInteraction
    InteractionApprovalState <|-- InteractionApproval
    Interaction <|-- InteractionApproval
    User <|-- InteractionApproval
    Validation <|-- ValidationParameter
    Validation <|-- ValidationApproval
    Question <|-- QuestionHasValidation
    Scenario <|-- ScenarioData
    Scenario <|-- ScenarioHasFeature
    Feature <|-- ScenarioHasFeature
    FeatureStep <|-- ScenarioInfo
    Question <|-- FeatureStep
    Task <|-- FeatureStep
    ScenarioData <|-- RawData
    RawData <|-- FieldType
```

Este diagrama resume las relaciones principales entre las entidades. Las flechas indican dependencias mediante claves foráneas. De esta forma puede verse cómo los usuarios se vinculan a roles y permisos, los clientes a sus proyectos y activos digitales, y los escenarios a sus datos de prueba.
