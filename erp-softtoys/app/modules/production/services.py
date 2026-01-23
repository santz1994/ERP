from sqlalchemy.orm import Session

from . import models, schemas


def create_mo(db: Session, mo: schemas.MOCreate):
    # Contoh Logic: Validasi apakah Article Code valid (Bisa cek ke Master Data)
    # if not check_article_exists(mo.article_code):
    #     raise HTTPException(status_code=400, detail="Article tidak ditemukan")

    db_mo = models.ManufacturingOrder(
        po_number=mo.po_number,
        article_code=mo.article_code,
        qty_planned=mo.qty_planned,
        routing_type=mo.routing_type
    )
    db.add(db_mo)
    db.commit()
    db.refresh(db_mo)
    return db_mo

# REMOVED: check_line_clearance() - Unused standalone function
# Use BaseProductionService.check_line_clearance() instead (app/core/base_production_service.py)
