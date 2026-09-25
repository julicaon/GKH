from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from application.use_cases.buildings import ListBuildingsForResident, ResolveBuilding
from application.use_cases.triage import ListAvailableCategoriesForBuilding
from domain.exceptions import BuildingNotFoundError, ValidationError
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


class ResolveBuildingIn(BaseModel):
    buildingId: Optional[str] = None
    addressQuery: Optional[str] = Field(
        default=None, description="Свободный ввод адреса для маппинга на seed Building"
    )


@router.get("", response_model=list[BuildingOut])
def list_buildings(db: Session = Depends(get_db)):
    r = repos(db)
    items = ListBuildingsForResident(buildings=r["buildings"]).execute()
    return [building_out(b) for b in items]


@router.post("/resolve", response_model=BuildingOut)
def resolve_building(body: ResolveBuildingIn, db: Session = Depends(get_db)):
    r = repos(db)
    try:
        building = ResolveBuilding(buildings=r["buildings"]).execute(
            building_id=body.buildingId,
            address_query=body.addressQuery,
        )
    except BuildingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return building_out(building)


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
