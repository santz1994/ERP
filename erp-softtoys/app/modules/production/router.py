from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from . import schemas, services

router = APIRouter(
    prefix="/production",
    tags=["Production Execution"]
)

@router.post("/create-mo", response_model=schemas.MOResponse)
def create_manufacturing_order(mo: schemas.MOCreate, db: Session = Depends(get_db)):
    return services.create_mo(db=db, mo=mo)

@router.get("/check-clearance/{line_id}")
def check_line(line_id: str):
    is_clear = services.check_line_clearance(line_id)
    if not is_clear:
        raise HTTPException(status_code=400, detail="Line Masih Sibuk! Lakukan Clearance.")
    return {"status": "Line Clear", "line_id": line_id}
