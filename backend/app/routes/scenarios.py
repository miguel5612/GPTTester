from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, deps, crypto
from ..crud import create_crud_router

router = create_crud_router("scenarios", models.Scenario, schemas.Scenario)

data_router = APIRouter(prefix="/scenarios", tags=["scenariodata"])
perm_sd = lambda m: Depends(deps.require_api_permission("/scenariodata", m))
perm_raw = lambda m: Depends(deps.require_api_permission("/rawdata", m))


@router.put(
    "/{scenario_id}/status",
    response_model=schemas.Scenario,
    dependencies=[Depends(deps.require_api_permission("/scenarios", "PUT"))],
)
def update_scenario_status(
    scenario_id: int, body: dict, db: Session = Depends(deps.get_db)
):
    scenario = db.query(models.Scenario).filter_by(id=scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    new_status = bool(body.get("status"))
    if new_status and not _scenario_ready(db, scenario_id):
        raise HTTPException(status_code=409, detail="Scenario incomplete")
    scenario.status = new_status
    db.commit()
    db.refresh(scenario)
    return scenario


def _scenario_ready(db: Session, scenario_id: int) -> bool:
    infos = db.query(models.ScenarioInfo).filter_by(scenarioId=scenario_id).all()
    if not infos:
        return False
    for info in infos:
        step = db.query(models.FeatureStep).filter_by(id=info.featureStepId).first()
        if not step or (step.taskId is None and step.questionId is None):
            return False
    return True


@data_router.get(
    "/{scenario_id}/data",
    response_model=list[schemas.ScenarioData],
    dependencies=[perm_sd("GET")],
)
def list_scenario_data(scenario_id: int, db: Session = Depends(deps.get_db)):
    if not db.query(models.Scenario).filter_by(id=scenario_id).first():
        raise HTTPException(status_code=404, detail="Scenario not found")
    return db.query(models.ScenarioData).filter_by(idScenario=scenario_id).all()


@data_router.post(
    "/{scenario_id}/data",
    response_model=schemas.ScenarioData,
    dependencies=[perm_sd("POST")],
)
def create_scenario_data(
    scenario_id: int, data: schemas.ScenarioData, db: Session = Depends(deps.get_db)
):
    if not db.query(models.Scenario).filter_by(id=scenario_id).first():
        raise HTTPException(status_code=404, detail="Scenario not found")
    obj = models.ScenarioData(idScenario=scenario_id, status=data.status)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@data_router.get(
    "/data/{data_id}/raw",
    response_model=list[schemas.RawData],
    dependencies=[perm_raw("GET")],
)
def list_raw_data(data_id: int, db: Session = Depends(deps.get_db)):
    if not db.query(models.ScenarioData).filter_by(id=data_id).first():
        raise HTTPException(status_code=404, detail="ScenarioData not found")
    objs = db.query(models.RawData).filter_by(scenarioDataId=data_id).all()
    for o in objs:
        if o.fieldValue is not None:
            o.fieldValue = crypto.decrypt(o.fieldValue)
    return objs


@data_router.post(
    "/data/{data_id}/raw",
    response_model=schemas.RawData,
    dependencies=[perm_raw("POST")],
)
def create_raw_data(
    data_id: int, raw: schemas.RawData, db: Session = Depends(deps.get_db)
):
    sd = db.query(models.ScenarioData).filter_by(id=data_id).first()
    ft = db.query(models.FieldType).filter_by(id=raw.fieldTypeId).first()
    if not sd or not ft:
        raise HTTPException(
            status_code=404, detail="ScenarioData or FieldType not found"
        )
    data = raw.dict()
    if data.get("fieldValue") is not None:
        data["fieldValue"] = crypto.encrypt(data["fieldValue"])
    obj = models.RawData(**data, scenarioDataId=data_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    if obj.fieldValue is not None:
        obj.fieldValue = crypto.decrypt(obj.fieldValue)
    return obj


router.include_router(data_router)
