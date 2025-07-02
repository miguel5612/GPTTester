from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

# 1️⃣ Roles
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role")
    page_permissions = relationship("PagePermission", back_populates="role")
    api_permissions = relationship("ApiPermission", back_populates="role")


# 2️⃣ Users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    endSubscriptionDate = Column(DateTime)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    dedication = Column(Integer)

    role = relationship("Role", back_populates="users")


# 3️⃣ Execution
class Execution(Base):
    __tablename__ = 'executions'
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    launchDate = Column(DateTime)
    endDate = Column(DateTime)
    status = Column(String(50))
    is_active = Column(Boolean, default=True)

    user = relationship("User")


# 4️⃣ Report
class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    executionId = Column(Integer, ForeignKey('executions.id'), nullable=False)
    result = Column(String(100))
    summary = Column(Text)

    execution = relationship("Execution")


# 5️⃣ Step
class Step(Base):
    __tablename__ = 'steps'
    id = Column(Integer, primary_key=True, index=True)
    reportId = Column(Integer, ForeignKey('reports.id'), nullable=False)
    result = Column(String(100))
    summary = Column(Text)

    report = relationship("Report")


# 6️⃣ Evidence
class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(Integer, primary_key=True, index=True)
    stepId = Column(Integer, ForeignKey('steps.id'), nullable=False)
    location = Column(String(200))
    base64IMG = Column(Text)
    summary = Column(Text)

    step = relationship("Step")


# 7️⃣ PagePermissions
class PagePermission(Base):
    __tablename__ = 'page_permissions'
    id = Column(Integer, primary_key=True, index=True)
    page = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    isStartPage = Column(Boolean, default=False)
    description = Column(Text)

    role = relationship("Role", back_populates="page_permissions")


# 8️⃣ ApiPermissions
class ApiPermission(Base):
    __tablename__ = 'api_permissions'
    id = Column(Integer, primary_key=True, index=True)
    route = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    description = Column(Text)

    role = relationship("Role", back_populates="api_permissions")


# 9️⃣ Clients
class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    idGerente = Column(Integer)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    mision = Column(Text)
    vision = Column(Text)
    paginaInicio = Column(String(200))
    dedication = Column(Integer)


# 🔟 BusinessAgreements
class BusinessAgreement(Base):
    __tablename__ = 'business_agreements'
    id = Column(Integer, primary_key=True, index=True)
    clientId = Column(Integer, ForeignKey('clients.id'), nullable=False)
    description = Column(Text)
    okr = Column(Text)
    kpi = Column(Text)


# 1️⃣1️⃣ DigitalAssets
class DigitalAsset(Base):
    __tablename__ = 'digital_assets'
    id = Column(Integer, primary_key=True, index=True)
    clientId = Column(Integer, ForeignKey('clients.id'), nullable=False)
    description = Column(Text)
    okr = Column(Text)
    kpi = Column(Text)


# 1️⃣2️⃣ UserInterface
class UserInterface(Base):
    __tablename__ = 'user_interfaces'
    id = Column(Integer, primary_key=True, index=True)
    digitalAssetsId = Column(Integer, ForeignKey('digital_assets.id'), nullable=False)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 1️⃣3️⃣ ElementType
class ElementType(Base):
    __tablename__ = 'element_types'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 1️⃣4️⃣ Element
class Element(Base):
    __tablename__ = 'elements'
    id = Column(Integer, primary_key=True, index=True)
    userInterfaceId = Column(Integer, ForeignKey('user_interfaces.id'), nullable=False)
    elementTypeId = Column(Integer, ForeignKey('element_types.id'), nullable=False)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 1️⃣5️⃣ Projects
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    digitalAssetsId = Column(Integer, ForeignKey('digital_assets.id'), nullable=False)
    name = Column(String(200), nullable=False)
    objective = Column(Text)
    is_active = Column(Boolean, default=True)
    scripts_per_day = Column(Integer)


# 1️⃣6️⃣ ProjectEmployee
class ProjectEmployee(Base):
    __tablename__ = 'project_employees'
    id = Column(Integer, primary_key=True, index=True)
    projectId = Column(Integer, ForeignKey('projects.id'), nullable=False)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    objective = Column(Text)
    dedicationHours = Column(Integer)


# 1️⃣7️⃣ Actors
class Actor(Base):
    __tablename__ = 'actors'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    habilitiesId = Column(Integer, ForeignKey('habilities.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)


# 1️⃣8️⃣ Habilities
class Hability(Base):
    __tablename__ = 'habilities'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)


# 1️⃣9️⃣ Interactions
class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    code = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    requireReview = Column(Boolean, default=False)
    description = Column(Text)


# 2️⃣0️⃣ InteractionParameters
class InteractionParameter(Base):
    __tablename__ = 'interaction_parameters'
    id = Column(Integer, primary_key=True, index=True)
    interactionId = Column(Integer, ForeignKey('interactions.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    direction = Column(Boolean, default=True)


# 2️⃣1️⃣ InteractionApprovalState
class InteractionApprovalState(Base):
    __tablename__ = 'interaction_approval_states'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)


# 2️⃣2️⃣ InteractionApproval
class InteractionApproval(Base):
    __tablename__ = 'interaction_approvals'
    id = Column(Integer, primary_key=True, index=True)
    interactionId = Column(Integer, ForeignKey('interactions.id'), nullable=False)
    creatorId = Column(Integer, ForeignKey('users.id'), nullable=False)
    aprovalUserId = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text)
    interactionAprovalStateId = Column(Integer, ForeignKey('interaction_approval_states.id'), nullable=False)
    aprovalDate = Column(DateTime)
    creationDate = Column(DateTime)


# 2️⃣3️⃣ Task
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 2️⃣4️⃣ TaskHaveInteraction
class TaskHaveInteraction(Base):
    __tablename__ = 'task_have_interactions'
    id = Column(Integer, primary_key=True, index=True)
    taskId = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    interactionId = Column(Integer, ForeignKey('interactions.id'), nullable=False)
    status = Column(Boolean, default=True)


# 2️⃣5️⃣ Validation
class Validation(Base):
    __tablename__ = 'validations'
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey('users.id'), nullable=False)
    code = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    requireReview = Column(Boolean, default=False)
    description = Column(Text)


# 2️⃣6️⃣ ValidationParameters
class ValidationParameter(Base):
    __tablename__ = 'validation_parameters'
    id = Column(Integer, primary_key=True, index=True)
    interactionId = Column(Integer, ForeignKey('validations.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    direction = Column(Boolean, default=True)


# 2️⃣7️⃣ ValidationApproval
class ValidationApproval(Base):
    __tablename__ = 'validation_approvals'
    id = Column(Integer, primary_key=True, index=True)
    validationId = Column(Integer, ForeignKey('validations.id'), nullable=False)
    creatorId = Column(Integer, ForeignKey('users.id'), nullable=False)
    aprovalUserId = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text)
    interactionAprovalStateId = Column(Integer, ForeignKey('interaction_approval_states.id'), nullable=False)
    aprovalDate = Column(DateTime)
    creationDate = Column(DateTime)


# 2️⃣8️⃣ Question
class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 2️⃣9️⃣ QuestionHasValidation
class QuestionHasValidation(Base):
    __tablename__ = 'question_has_validations'
    id = Column(Integer, primary_key=True, index=True)
    validationId = Column(Integer, ForeignKey('validations.id'), nullable=False)
    questionId = Column(Integer, ForeignKey('questions.id'), nullable=False)


# 3️⃣0️⃣ Scenario
class Scenario(Base):
    __tablename__ = 'scenarios'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 3️⃣1️⃣ ScenarioData
class ScenarioData(Base):
    __tablename__ = 'scenario_data'
    id = Column(Integer, primary_key=True, index=True)
    idScenario = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    status = Column(Boolean, default=True)


# 3️⃣2️⃣ RawData
class RawData(Base):
    __tablename__ = 'raw_data'
    id = Column(Integer, primary_key=True, index=True)
    fieldTypeId = Column(Integer, ForeignKey('field_types.id'), nullable=False)
    fieldName = Column(String(200), nullable=False)
    fieldValue = Column(String(500))
    autoGenerated = Column(Boolean, default=False)
    scenarioDataId = Column(Integer, ForeignKey('scenario_data.id'), nullable=False)
    length = Column(String(100))
    status = Column(Boolean, default=True)


# 3️⃣3️⃣ FieldType
class FieldType(Base):
    __tablename__ = 'field_types'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    format = Column(String(100))
    description = Column(Text)
    status = Column(Boolean, default=True)


# 3️⃣4️⃣ Feature
class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Boolean, default=True)


# 3️⃣5️⃣ ScenarioHasFeature
class ScenarioHasFeature(Base):
    __tablename__ = 'scenario_has_features'
    id = Column(Integer, primary_key=True, index=True)
    featureId = Column(Integer, ForeignKey('features.id'), nullable=False)
    scenarioId = Column(Integer, ForeignKey('scenarios.id'), nullable=False)


# 3️⃣6️⃣ FeatureStep
class FeatureStep(Base):
    __tablename__ = 'feature_steps'
    id = Column(Integer, primary_key=True, index=True)
    GherkinStep = Column(Text, nullable=False)
    questionId = Column(Integer, ForeignKey('questions.id'))
    taskId = Column(Integer, ForeignKey('tasks.id'))


# 3️⃣7️⃣ ScenarioInfo
class ScenarioInfo(Base):
    __tablename__ = 'scenario_info'
    id = Column(Integer, primary_key=True, index=True)
    featureStepId = Column(Integer, ForeignKey('feature_steps.id'), nullable=False)
    scenarioId = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    order = Column(Integer)
    status = Column(Boolean, default=True)
