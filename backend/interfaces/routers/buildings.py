from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from application.use_cases.buildings import ListBuildingsForResident
from application.use_cases.triage import ListAvailableCategoriesForBuilding
from domain.exceptions import BuildingNotFoundError
from fastapi import HTTPException
from interfaces.deps import get_db, repos
from interfaces.schemas import (
    BuildingCategoriesOut,
    BuildingOut,
    CategoryTreeNode,
    building_out,
    category_out,
    parent_out,
)

router = APIRouter(prefix="/api/buildings", tags=["buildings"])


@router.get("", response_model=list[BuildingOut])
def list_buildings(db: Session = Depends(get_db)):
    r = repos(db)
    items = ListBuildingsForResident(buildings=r["buildings"]).execute()
    return [building_out(b) for b in items]


@router.get("/{building_id}/categories", response_model=BuildingCategoriesOut)
def building_categories(building_id: str, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        result = ListAvailableCategoriesForBuilding(
            buildings=r["buildings"], categories=r["categories"]
        ).execute(building_id)
    except BuildingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    tree = [
        CategoryTreeNode(
            parent=parent_out(node["parent"]),
            categories=[category_out(c) for c in node["categories"]],
        )
        for node in result["tree"]
    ]
    return BuildingCategoriesOut(building=building_out(result["building"]), tree=tree)
