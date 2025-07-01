from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import engine
from . import models, schemas, deps
from .crud import create_crud_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Test Automation API")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    user = deps.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = deps.create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# CRUD routers for main entities
def register_cruds():
    mappings = [
        ("roles", models.Role, schemas.Role),
        ("users", models.User, schemas.User),
        ("pagepermissions", models.PagePermission, schemas.PagePermission),
        ("apipermissions", models.ApiPermission, schemas.ApiPermission),
        ("clients", models.Client, schemas.Client),
        ("businessagreements", models.BusinessAgreement, schemas.BusinessAgreement),
        ("digitalassets", models.DigitalAsset, schemas.DigitalAsset),
        ("userinterfaces", models.UserInterface, schemas.UserInterface),
        ("elementtypes", models.ElementType, schemas.ElementType),
        ("elements", models.Element, schemas.Element),
        ("projects", models.Project, schemas.Project),
        ("projectemployees", models.ProjectEmployee, schemas.ProjectEmployee),
        ("actors", models.Actor, schemas.Actor),
        ("habilities", models.Hability, schemas.Hability),
        ("interactions", models.Interaction, schemas.Interaction),
        ("interactionparameters", models.InteractionParameter, schemas.InteractionParameter),
        ("interactionapprovalstates", models.InteractionApprovalState, schemas.InteractionApprovalState),
        ("interactionapprovals", models.InteractionApproval, schemas.InteractionApproval),
        ("tasks", models.Task, schemas.Task),
        ("taskhaveinteractions", models.TaskHaveInteraction, schemas.TaskHaveInteraction),
        ("validations", models.Validation, schemas.Validation),
        ("validationparameters", models.ValidationParameter, schemas.ValidationParameter),
        ("validationapprovals", models.ValidationApproval, schemas.ValidationApproval),
        ("questions", models.Question, schemas.Question),
        ("questionhasvalidations", models.QuestionHasValidation, schemas.QuestionHasValidation),
        ("scenarios", models.Scenario, schemas.Scenario),
        ("scenariodata", models.ScenarioData, schemas.ScenarioData),
        ("rawdata", models.RawData, schemas.RawData),
        ("fieldtypes", models.FieldType, schemas.FieldType),
        ("features", models.Feature, schemas.Feature),
        ("scenariohasfeatures", models.ScenarioHasFeature, schemas.ScenarioHasFeature),
        ("featuresteps", models.FeatureStep, schemas.FeatureStep),
        ("scenarioinfo", models.ScenarioInfo, schemas.ScenarioInfo),
    ]
    for prefix, model, schema in mappings:
        app.include_router(create_crud_router(prefix, model, schema))

register_cruds()
