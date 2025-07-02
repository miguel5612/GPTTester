from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, deps, crypto
from ..crud import create_crud_router

router = create_crud_router("features", models.Feature, schemas.Feature)

perm_shf = lambda m: Depends(deps.require_api_permission("/scenariohasfeatures", m))
perm_fs = lambda m: Depends(deps.require_api_permission("/featuresteps", m))
perm_si = lambda m: Depends(deps.require_api_permission("/scenarioinfo", m))


@router.get("/{feature_id}/scenarios", dependencies=[perm_shf("GET")])
def list_feature_scenarios(feature_id: int, db: Session = Depends(deps.get_db)):
    if not db.query(models.Feature).filter_by(id=feature_id).first():
        raise HTTPException(status_code=404, detail="Feature not found")
    links = db.query(models.ScenarioHasFeature).filter_by(featureId=feature_id).all()
    return links


@router.post(
    "/{feature_id}/scenarios/{scenario_id}",
    response_model=schemas.ScenarioHasFeature,
    dependencies=[perm_shf("POST")],
)
def add_feature_scenario(
    feature_id: int, scenario_id: int, db: Session = Depends(deps.get_db)
):
    feature = db.query(models.Feature).filter_by(id=feature_id).first()
    scenario = db.query(models.Scenario).filter_by(id=scenario_id).first()
    if not feature or not scenario:
        raise HTTPException(status_code=404, detail="Feature or scenario not found")
    existing = (
        db.query(models.ScenarioHasFeature)
        .filter_by(featureId=feature_id, scenarioId=scenario_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Relation already exists")
    obj = models.ScenarioHasFeature(featureId=feature_id, scenarioId=scenario_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/{feature_id}/scenarios/{scenario_id}", dependencies=[perm_shf("DELETE")]
)
def remove_feature_scenario(
    feature_id: int, scenario_id: int, db: Session = Depends(deps.get_db)
):
    link = (
        db.query(models.ScenarioHasFeature)
        .filter_by(featureId=feature_id, scenarioId=scenario_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Relation not found")
    db.delete(link)
    db.commit()
    return {"ok": True}


# CRUD for FeatureStep
step_router = create_crud_router(
    "featuresteps", models.FeatureStep, schemas.FeatureStep
)
router.include_router(step_router)

# CRUD for ScenarioInfo with validation
info_router = APIRouter(prefix="/scenarioinfo", tags=["scenarioinfo"])


@info_router.post(
    "/", response_model=schemas.ScenarioInfo, dependencies=[perm_si("POST")]
)
def create_info(info: schemas.ScenarioInfo, db: Session = Depends(deps.get_db)):
    step = db.query(models.FeatureStep).filter_by(id=info.featureStepId).first()
    scenario = db.query(models.Scenario).filter_by(id=info.scenarioId).first()
    if not step or not scenario:
        raise HTTPException(status_code=404, detail="Step or scenario not found")
    obj = models.ScenarioInfo(**info.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@info_router.get(
    "/", response_model=list[schemas.ScenarioInfo], dependencies=[perm_si("GET")]
)
def list_info(db: Session = Depends(deps.get_db)):
    return db.query(models.ScenarioInfo).all()


router.include_router(info_router)
