from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 1️⃣ Roles
class Role(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool = True

    class Config:
        orm_mode = True


# 2️⃣ Users
class User(BaseModel):
    id: int
    username: str
    password: str
    last_login: Optional[datetime]
    is_active: bool
    endSubscriptionDate: Optional[datetime]
    role_id: int

    class Config:
        orm_mode = True


class UserActiveUpdate(BaseModel):
    is_active: bool


# 3️⃣ PagePermissions
class PagePermission(BaseModel):
    id: int
    page: str
    role_id: int
    isStartPage: bool
    description: str

    class Config:
        orm_mode = True


# 4️⃣ ApiPermissions
class ApiPermission(BaseModel):
    id: int
    route: str
    method: str
    role_id: int
    description: str

    class Config:
        orm_mode = True


class PagePermissionInput(BaseModel):
    page: str
    isStartPage: bool = False
    description: str = ""


class ApiPermissionInput(BaseModel):
    route: str
    method: str
    description: str = ""


# 5️⃣ Clients
class Client(BaseModel):
    id: int
    idGerente: Optional[int]
    name: str
    is_active: bool
    mision: str
    vision: str
    paginaInicio: str
    dedication: Optional[int]
    analysts: Optional[list[User]] = []

    class Config:
        orm_mode = True


# 6️⃣ BusinessAgreements
class BusinessAgreement(BaseModel):
    id: int
    clientId: int
    description: str
    okr: str
    kpi: str

    class Config:
        orm_mode = True


class ClientAnalyst(BaseModel):
    id: int
    clientId: int
    userId: int
    dedication: Optional[int]

    class Config:
        orm_mode = True


# 7️⃣ DigitalAssets
class DigitalAsset(BaseModel):
    id: int
    clientId: int
    description: str
    okr: str
    kpi: str

    class Config:
        orm_mode = True


# 8️⃣ UserInterface
class UserInterface(BaseModel):
    id: int
    digitalAssetsId: int
    description: str
    status: bool

    class Config:
        orm_mode = True


# 9️⃣ ElementType
class ElementType(BaseModel):
    id: int
    description: str
    status: bool

    class Config:
        orm_mode = True


# 🔟 Element
class Element(BaseModel):
    id: int
    userInterfaceId: int
    elementTypeId: int
    description: str
    status: bool

    class Config:
        orm_mode = True


# 11️⃣ Projects
class Project(BaseModel):
    id: int
    digitalAssetsId: int
    name: str
    objective: Optional[str]
    is_active: bool
    scripts_per_day: Optional[int]
    analysts: Optional[list[User]] = []

    class Config:
        orm_mode = True


# 12️⃣ ProjectEmployee
class ProjectEmployee(BaseModel):
    id: int
    projectId: int
    userId: int
    objective: Optional[str]
    dedicationHours: Optional[int]

    class Config:
        orm_mode = True


# 13️⃣ Actors
class Actor(BaseModel):
    id: int
    name: str
    habilitiesId: int
    client_id: int

    class Config:
        orm_mode = True


# 14️⃣ Habilities
class Hability(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# 15️⃣ Interactions
class Interaction(BaseModel):
    id: int
    userId: int
    code: str
    name: str
    requireReview: bool
    description: str

    class Config:
        orm_mode = True


# 16️⃣ InteractionParameters
class InteractionParameter(BaseModel):
    id: int
    interactionId: int
    name: str
    description: str
    direction: bool

    class Config:
        orm_mode = True


# 17️⃣ InteractionApprovalState
class InteractionApprovalState(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


# 18️⃣ InteractionApproval
class InteractionApproval(BaseModel):
    id: int
    interactionId: int
    creatorId: int
    aprovalUserId: int
    comment: str
    interactionAprovalStateId: int
    aprovalDate: Optional[datetime]
    creationDate: Optional[datetime]

    class Config:
        orm_mode = True


class InteractionCreate(BaseModel):
    userId: int
    code: str
    name: str
    requireReview: bool = False
    description: str


class InteractionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    requireReview: Optional[bool] = None
    description: Optional[str] = None


class InteractionParameterCreate(BaseModel):
    interactionId: int
    name: str
    description: str
    direction: bool = True


class InteractionParameterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    direction: Optional[bool] = None


class InteractionApprovalCreate(BaseModel):
    interactionId: int
    creatorId: int
    aprovalUserId: int
    comment: str
    interactionAprovalStateId: int


class InteractionApprovalUpdate(BaseModel):
    aprovalUserId: Optional[int] = None
    comment: Optional[str] = None
    interactionAprovalStateId: Optional[int] = None


# 19️⃣ Task
class Task(BaseModel):
    id: int
    name: str
    description: str
    status: bool

    class Config:
        orm_mode = True


# 20️⃣ TaskHaveInteractions
class TaskHaveInteraction(BaseModel):
    id: int
    taskId: int
    interactionId: int
    status: bool

    class Config:
        orm_mode = True


# 21️⃣ Validation
class Validation(BaseModel):
    id: int
    userId: int
    code: str
    name: str
    requireReview: bool
    description: str

    class Config:
        orm_mode = True


# 22️⃣ ValidationParameters
class ValidationParameter(BaseModel):
    id: int
    interactionId: int
    name: str
    description: str
    direction: bool

    class Config:
        orm_mode = True


# 23️⃣ ValidationApproval
class ValidationApproval(BaseModel):
    id: int
    validationId: int
    creatorId: int
    aprovalUserId: int
    comment: str
    interactionAprovalStateId: int
    aprovalDate: Optional[datetime]
    creationDate: Optional[datetime]

    class Config:
        orm_mode = True


class ValidationCreate(BaseModel):
    userId: int
    code: str
    name: str
    requireReview: bool = False
    description: str


class ValidationUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    requireReview: Optional[bool] = None
    description: Optional[str] = None


class ValidationParameterCreate(BaseModel):
    interactionId: int
    name: str
    description: str
    direction: bool = True


class ValidationParameterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    direction: Optional[bool] = None


class ValidationApprovalCreate(BaseModel):
    validationId: int
    creatorId: int
    aprovalUserId: int
    comment: str
    interactionAprovalStateId: int


class ValidationApprovalUpdate(BaseModel):
    aprovalUserId: Optional[int] = None
    comment: Optional[str] = None
    interactionAprovalStateId: Optional[int] = None


# 24️⃣ Question
class Question(BaseModel):
    id: int
    name: str
    description: str
    status: bool

    class Config:
        orm_mode = True


# 25️⃣ QuestionHasValidation
class QuestionHasValidation(BaseModel):
    id: int
    validationId: int
    questionId: int

    class Config:
        orm_mode = True


# 26️⃣ Scenario
class Scenario(BaseModel):
    id: int
    name: str
    description: str
    status: bool

    class Config:
        orm_mode = True


# 27️⃣ ScenarioData
class ScenarioData(BaseModel):
    id: int
    idScenario: int
    status: bool

    class Config:
        orm_mode = True


# 28️⃣ RawData
class RawData(BaseModel):
    id: int
    fieldTypeId: int
    fieldName: str
    fieldValue: Optional[str]
    autoGenerated: bool
    scenarioDataId: int
    length: Optional[str]
    status: bool

    class Config:
        orm_mode = True


# 29️⃣ FieldType
class FieldType(BaseModel):
    id: int
    name: str
    format: Optional[str]
    description: str
    status: bool

    class Config:
        orm_mode = True


# 30️⃣ Feature
class Feature(BaseModel):
    id: int
    name: str
    description: str
    status: bool

    class Config:
        orm_mode = True


# 31️⃣ ScenarioHasFeature
class ScenarioHasFeature(BaseModel):
    id: int
    featureId: int
    scenarioId: int

    class Config:
        orm_mode = True


# 32️⃣ FeatureStep
class FeatureStep(BaseModel):
    id: int
    GherkinStep: str
    questionId: Optional[int]
    taskId: Optional[int]

    class Config:
        orm_mode = True


# 33️⃣ ScenarioInfo
class ScenarioInfo(BaseModel):
    id: int
    featureStepId: int
    scenarioId: int
    order: Optional[int]
    status: bool

    class Config:
        orm_mode = True
