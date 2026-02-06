"""Masterdata Import API Endpoints - Session 49 Phase 8
FastAPI router for bulk masterdata imports with Excel template support.

Endpoints:
- POST /imports/suppliers - Upload suppliers Excel
- POST /imports/materials - Upload materials Excel
- POST /imports/articles - Upload articles Excel
- POST /imports/bom - Upload BOM Excel
- GET /imports/templates/{type} - Download Excel template
- GET /imports/history - View import history (future)
"""
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.models.users import User
from app.services.masterdata_import_service import MasterdataImportService

router = APIRouter(prefix="/imports", tags=["Masterdata Import"])


# ====================== IMPORT ENDPOINTS ======================

@router.post(
    "/suppliers",
    dependencies=[Depends(require_permission("masterdata.import"))],
    summary="Import suppliers from Excel"
)
async def import_suppliers(
    file: UploadFile = File(..., description="Excel file (.xlsx) with suppliers data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("masterdata.import"))
):
    """Import suppliers from Excel template.
    
    **Excel Format**:
    - supplier_code (required)
    - supplier_name (required)
    - supplier_type (required): SUPPLIER, SUBCON, CUSTOMER
    - contact_person (optional)
    - phone (optional)
    - email (optional)
    - address (optional)
    - notes (optional)

    **Processing**:
    - Validates all data before insertion
    - UPDATE mode: Existing suppliers are updated
    - Transaction-safe: Rolls back on ANY error
    - Returns detailed error report with row numbers

    **Returns**:
    ```json
    {
        "success": true,
        "imported_count": 15,
        "updated_count": 3,
        "errors": [],
        "execution_time_ms": 1234
    }
    ```
    """
    # Validate file extension
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be Excel format (.xlsx or .xls)"
        )

    # Read file content
    content = await file.read()

    # Execute import
    service = MasterdataImportService(db, current_user.id)
    result = service.import_suppliers(content)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Import failed. Please fix errors and try again.",
                "errors": result["errors"],
                "imported_count": result["imported_count"],
                "updated_count": result["updated_count"]
            }
        )

    return result


@router.post(
    "/materials",
    dependencies=[Depends(require_permission("masterdata.import"))],
    summary="Import materials from Excel"
)
async def import_materials(
    file: UploadFile = File(..., description="Excel file (.xlsx) with materials data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("masterdata.import"))
):
    """Import materials from Excel template.
    
    **Excel Format**:
    - material_code (required)
    - material_name (required)
    - material_type (required): RAW_MATERIAL, BAHAN_PENOLONG, WIP, FINISHED_GOODS
    - uom (required): PCS, YARD, METER, KG, GRAM, CONE, ROLL, BOX, CARTON
    - category (required): Must match existing category name
    - minimum_stock (optional): Default 0
    - notes (optional)

    **Processing**:
    - Validates material_type and uom enums
    - Checks if category exists in database
    - UPDATE mode for existing materials
    - Transaction-safe rollback

    **Returns**:
    ```json
    {
        "success": true,
        "imported_count": 250,
        "updated_count": 10,
        "errors": [],
        "execution_time_ms": 3456
    }
    ```
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be Excel format (.xlsx or .xls)"
        )

    content = await file.read()

    service = MasterdataImportService(db, current_user.id)
    result = service.import_materials(content)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Import failed. Please fix errors and try again.",
                "errors": result["errors"],
                "imported_count": result["imported_count"],
                "updated_count": result["updated_count"]
            }
        )

    return result


@router.post(
    "/articles",
    dependencies=[Depends(require_permission("masterdata.import"))],
    summary="Import articles from Excel"
)
async def import_articles(
    file: UploadFile = File(..., description="Excel file (.xlsx) with articles data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("masterdata.import"))
):
    """Import articles (finished goods) from Excel template.
    
    **Excel Format**:
    - article_code (required): IKEA code or internal code
    - article_name (required)
    - description (optional)
    - buyer (optional): e.g., IKEA
    - category (required): Must match existing category
    - standard_packing (optional): Pcs per carton
    - parent_article_code (optional): For parent-child relationship
    - notes (optional)

    **Note**: Articles are essentially Products with type=FINISHED_GOODS.
    This endpoint is a convenience wrapper for importing finished goods specifically.

    **Returns**:
    ```json
    {
        "success": true,
        "imported_count": 45,
        "updated_count": 2,
        "errors": [],
        "execution_time_ms": 987
    }
    ```
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be Excel format (.xlsx or .xls)"
        )

    content = await file.read()

    # Articles are products with type=FINISHED_GOODS
    # For now, redirect to materials import with type override (future enhancement)
    service = MasterdataImportService(db, current_user.id)
    
    # TODO: Implement dedicated article import logic
    # For now, use materials import
    raise HTTPException(
        status_code=501,
        detail="Article import endpoint not yet implemented. Use materials import with type=FINISHED_GOODS for now."
    )


@router.post(
    "/bom",
    dependencies=[Depends(require_permission("masterdata.import"))],
    summary="Import BOM (Bill of Materials) from Excel"
)
async def import_bom(
    file: UploadFile = File(..., description="Excel file (.xlsx) with BOM data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("masterdata.import"))
):
    """Import BOM structures from Excel template.
    
    **Excel Format**:
    - article_code (required): Must exist in products table
    - component_code (required): Must exist in products table
    - quantity_required (required): Qty per 1 unit of article
    - wastage_percent (optional): 0-100, default 0
    - notes (optional)

    **Processing**:
    - Groups by article_code to create BOM headers
    - Creates BOM details for each row
    - UPDATE mode: Existing BOM lines updated
    - Validates both article and component exist

    **Critical**:
    - Must import materials/articles FIRST before BOM
    - BOM import will fail if referenced products don't exist

    **Returns**:
    ```json
    {
        "success": true,
        "imported_count": 850,
        "updated_count": 50,
        "errors": [],
        "execution_time_ms": 5678
    }
    ```
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be Excel format (.xlsx or .xls)"
        )

    content = await file.read()

    service = MasterdataImportService(db, current_user.id)
    result = service.import_bom(content)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Import failed. Please fix errors and try again.",
                "errors": result["errors"],
                "imported_count": result["imported_count"],
                "updated_count": result["updated_count"]
            }
        )

    return result


# ====================== TEMPLATE ENDPOINTS ======================

@router.get(
    "/templates/{import_type}",
    summary="Download Excel template for import"
)
async def download_template(
    import_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("masterdata.import"))
):
    """Download Excel template for specific import type.
    
    **Supported Types**:
    - suppliers
    - materials
    - articles
    - bom
    - supplier-materials (future)

    **Returns**: Excel file download (.xlsx)
    
    **Usage**:
    ```bash
    GET /api/v1/imports/templates/suppliers
    # Downloads: suppliers_template.xlsx with sample data
    ```
    """
    service = MasterdataImportService(db, current_user.id)

    if import_type == "suppliers":
        buffer = service.generate_suppliers_template()
        filename = "suppliers_template.xlsx"
    elif import_type == "materials":
        buffer = service.generate_materials_template()
        filename = "materials_template.xlsx"
    elif import_type == "articles":
        buffer = service.generate_articles_template()
        filename = "articles_template.xlsx"
    elif import_type == "bom":
        buffer = service.generate_bom_template()
        filename = "bom_template.xlsx"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid import type. Supported: suppliers, materials, articles, bom"
        )

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get(
    "/history",
    summary="Get import history (future feature)"
)
async def get_import_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("masterdata.import"))
):
    """Get import history with audit trail.
    
    **Future Enhancement**:
    - Query audit_logs table for import activities
    - Filter by user, date range, import type
    - Show success/failure status
    - Link to error logs

    **Returns**:
    ```json
    {
        "data": [
            {
                "id": 123,
                "import_type": "suppliers",
                "user": "admin",
                "imported_count": 15,
                "updated_count": 3,
                "errors_count": 0,
                "execution_time_ms": 1234,
                "created_at": "2026-02-06T10:30:00Z"
            }
        ],
        "total": 45,
        "skip": 0,
        "limit": 20
    }
    ```
    """
    # TODO: Implement audit trail query
    raise HTTPException(
        status_code=501,
        detail="Import history endpoint not yet implemented. Check audit_logs table directly for now."
    )
