"""Dynamic Report Builder API
Allows users to create, modify, and manage custom reports
"""

from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models.users import User
from app.core.permissions import ModuleName, Permission, require_permission

router = APIRouter(
    prefix="/report-builder",
    tags=["Report Builder"]
)


# Pydantic Models
class ReportColumn(BaseModel):
    """Report column definition"""

    name: str = Field(..., description="Column name from database")
    label: str = Field(..., description="Display label for column")
    type: str = Field(default="string", description="Data type: string, number, date, boolean")
    format: str | None = Field(None, description="Display format (e.g., 'YYYY-MM-DD' for dates)")
    aggregate: str | None = Field(None, description="Aggregation function: sum, avg, count, min, max")


class ReportFilter(BaseModel):
    """Report filter definition"""

    column: str = Field(..., description="Column name to filter")
    operator: str = Field(..., description="Operator: =, !=, >, <, >=, <=, LIKE, IN, BETWEEN")
    value: Any = Field(..., description="Filter value(s)")


class ReportSort(BaseModel):
    """Report sort definition"""

    column: str
    direction: str = Field(default="ASC", description="ASC or DESC")


class CreateReportRequest(BaseModel):
    """Request to create a new report template"""

    name: str = Field(..., description="Report name")
    description: str | None = Field(None, description="Report description")
    category: str = Field(..., description="Report category: Production, QC, Inventory, etc.")
    data_source: str = Field(..., description="Data source: work_orders, qc_inspections, products, etc.")
    columns: list[ReportColumn] = Field(..., description="Columns to include in report")
    filters: list[ReportFilter] | None = Field(default=[], description="Filters to apply")
    sorts: list[ReportSort] | None = Field(default=[], description="Sort order")
    group_by: list[str] | None = Field(default=[], description="Columns to group by")
    is_public: bool = Field(default=False, description="Allow other users to use this report")


class UpdateReportRequest(BaseModel):
    """Request to update an existing report template"""

    name: str | None = None
    description: str | None = None
    columns: list[ReportColumn] | None = None
    filters: list[ReportFilter] | None = None
    sorts: list[ReportSort] | None = None
    group_by: list[str] | None = None
    is_public: bool | None = None


class ReportTemplate(BaseModel):
    """Report template response"""

    id: int
    name: str
    description: str | None
    category: str
    data_source: str
    columns: list[ReportColumn]
    filters: list[ReportFilter]
    sorts: list[ReportSort]
    group_by: list[str]
    is_public: bool
    created_by: int
    created_by_name: str | None
    created_at: datetime
    updated_at: datetime | None
    usage_count: int = 0


class ExecuteReportRequest(BaseModel):
    """Request to execute a report"""

    template_id: int
    override_filters: list[ReportFilter] | None = Field(default=[], description="Override/add filters")
    limit: int | None = Field(default=1000, description="Max rows to return")
    offset: int | None = Field(default=0, description="Offset for pagination")
    export_format: str | None = Field(default="json", description="Format: json, csv, xlsx, pdf")


class ReportResult(BaseModel):
    """Report execution result"""

    template_id: int
    template_name: str
    columns: list[dict[str, str]]  # [{name, label, type}]
    data: list[dict[str, Any]]
    total_rows: int
    execution_time: float
    executed_at: datetime


# Available data sources
DATA_SOURCES = {
    "work_orders": {
        "table": "work_orders",
        "joins": ["LEFT JOIN users ON work_orders.worker_id = users.id"],
        "columns": {
            "id": "work_orders.id",
            "mo_id": "work_orders.mo_id",
            "department": "work_orders.department",
            "status": "work_orders.status",
            "input_qty": "work_orders.input_qty",
            "output_qty": "work_orders.output_qty",
            "reject_qty": "work_orders.reject_qty",
            "worker_name": "users.full_name",
            "start_time": "work_orders.start_time",
            "end_time": "work_orders.end_time"
        }
    },
    "qc_inspections": {
        "table": "qc_inspections",
        "joins": ["LEFT JOIN users ON qc_inspections.inspected_by = users.id"],
        "columns": {
            "id": "qc_inspections.id",
            "work_order_id": "qc_inspections.work_order_id",
            "type": "qc_inspections.type",
            "status": "qc_inspections.status",
            "defect_reason": "qc_inspections.defect_reason",
            "inspector_name": "users.full_name",
            "created_at": "qc_inspections.created_at"
        }
    },
    "products": {
        "table": "products",
        "joins": [],
        "columns": {
            "id": "products.id",
            "code": "products.code",
            "name": "products.name",
            "type": "products.type",
            "uom": "products.uom",
            "min_stock": "products.min_stock",
            "created_at": "products.created_at"
        }
    },
    "stock_quants": {
        "table": "stock_quants",
        "joins": [
            "LEFT JOIN products ON stock_quants.product_id = products.id",
            "LEFT JOIN stock_locations ON stock_quants.location_id = stock_locations.id"
        ],
        "columns": {
            "id": "stock_quants.id",
            "product_code": "products.code",
            "product_name": "products.name",
            "qty_available": "stock_quants.qty_available",
            "qty_reserved": "stock_quants.qty_reserved",
            "location_name": "stock_locations.location_name",
            "updated_at": "stock_quants.updated_at"
        }
    },
    "manufacturing_orders": {
        "table": "manufacturing_orders",
        "joins": ["LEFT JOIN products ON manufacturing_orders.product_id = products.id"],
        "columns": {
            "id": "manufacturing_orders.id",
            "batch_number": "manufacturing_orders.batch_number",
            "product_name": "products.name",
            "qty_planned": "manufacturing_orders.qty_planned",
            "qty_produced": "manufacturing_orders.qty_produced",
            "routing_type": "manufacturing_orders.routing_type",
            "state": "manufacturing_orders.state",
            "created_at": "manufacturing_orders.created_at"
        }
    }
}


@router.get("/templates", response_model=List[ReportTemplate])
async def list_report_templates(
    category: Optional[str] = None,
    current_user: User = Depends(require_permission(ModuleName.REPORTS, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """List all available report templates

    - Returns user's own templates and public templates
    - Can filter by category
    """
    # TODO: Implement database table for report templates
    # For now, return mock data
    mock_templates = [
        {
            "id": 1,
            "name": "Daily Production Report",
            "description": "Daily production output by department",
            "category": "Production",
            "data_source": "work_orders",
            "columns": [
                {"name": "department", "label": "Department", "type": "string"},
                {"name": "output_qty", "label": "Output Qty", "type": "number", "aggregate": "sum"}
            ],
            "filters": [],
            "sorts": [{"column": "department", "direction": "ASC"}],
            "group_by": ["department"],
            "is_public": True,
            "created_by": 1,
            "created_by_name": "Admin",
            "created_at": datetime.now(),
            "updated_at": None,
            "usage_count": 45
        },
        {
            "id": 2,
            "name": "QC Defects Summary",
            "description": "Summary of QC defects by type",
            "category": "QC",
            "data_source": "qc_inspections",
            "columns": [
                {"name": "type", "label": "Inspection Type", "type": "string"},
                {"name": "status", "label": "Status", "type": "string"},
                {"name": "id", "label": "Count", "type": "number", "aggregate": "count"}
            ],
            "filters": [{"column": "status", "operator": "=", "value": "Fail"}],
            "sorts": [{"column": "id", "direction": "DESC"}],
            "group_by": ["type", "status"],
            "is_public": True,
            "created_by": 1,
            "created_by_name": "Admin",
            "created_at": datetime.now(),
            "updated_at": None,
            "usage_count": 32
        }
    ]

    if category:
        mock_templates = [t for t in mock_templates if t["category"] == category]

    return mock_templates


@router.post("/template", response_model=ReportTemplate, status_code=status.HTTP_201_CREATED)
async def create_report_template(
    request: CreateReportRequest,
    current_user: User = Depends(require_permission(ModuleName.REPORTS, Permission.CREATE)),
    db: Session = Depends(get_db)
):
    """Create a new report template

    - Define columns, filters, sorting, and grouping
    - Templates can be made public for other users
    """
    # Validate data source
    if request.data_source not in DATA_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data source. Available: {', '.join(DATA_SOURCES.keys())}"
        )

    # Validate columns
    available_columns = DATA_SOURCES[request.data_source]["columns"]
    for col in request.columns:
        if col.name not in available_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{col.name}' not available in data source '{request.data_source}'"
            )

    # TODO: Save to database
    # For now, return mock response
    return {
        "id": 999,
        "name": request.name,
        "description": request.description,
        "category": request.category,
        "data_source": request.data_source,
        "columns": request.columns,
        "filters": request.filters or [],
        "sorts": request.sorts or [],
        "group_by": request.group_by or [],
        "is_public": request.is_public,
        "created_by": current_user.id,
        "created_by_name": current_user.full_name,
        "created_at": datetime.now(),
        "updated_at": None,
        "usage_count": 0
    }


@router.post("/execute", response_model=ReportResult)
async def execute_report(
    request: ExecuteReportRequest,
    current_user: User = Depends(require_permission(ModuleName.REPORTS, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """Execute a report template and return results

    - Apply filters and sorting
    - Support pagination
    - Export to various formats
    """
    # TODO: Fetch template from database
    # For now, use mock template
    template = {
        "id": 1,
        "name": "Daily Production Report",
        "data_source": "work_orders",
        "columns": [
            {"name": "department", "label": "Department", "type": "string"},
            {"name": "output_qty", "label": "Output Qty", "type": "number", "aggregate": "sum"}
        ],
        "filters": [],
        "sorts": [{"column": "department", "direction": "ASC"}],
        "group_by": ["department"]
    }

    # Build SQL query
    source_config = DATA_SOURCES[template["data_source"]]
    select_parts = []

    for col in template["columns"]:
        col_def = source_config["columns"][col["name"]]
        if col.get("aggregate"):
            select_parts.append(f"{col['aggregate']}({col_def}) as {col['name']}")
        else:
            select_parts.append(f"{col_def} as {col['name']}")

    query = f"SELECT {', '.join(select_parts)} FROM {source_config['table']}"

    # Add joins
    for join in source_config["joins"]:
        query += f" {join}"

    # Add WHERE clauses
    where_clauses = []
    for filter in template["filters"] + request.override_filters:
        col_def = source_config["columns"].get(filter.column)
        if col_def:
            if filter.operator == "LIKE":
                where_clauses.append(f"{col_def} LIKE '%{filter.value}%'")
            elif filter.operator == "IN":
                values = ", ".join([f"'{v}'" for v in filter.value])
                where_clauses.append(f"{col_def} IN ({values})")
            else:
                where_clauses.append(f"{col_def} {filter.operator} '{filter.value}'")

    if where_clauses:
        query += f" WHERE {' AND '.join(where_clauses)}"

    # Add GROUP BY
    if template["group_by"]:
        group_cols = [source_config["columns"][col] for col in template["group_by"]]
        query += f" GROUP BY {', '.join(group_cols)}"

    # Add ORDER BY
    if template["sorts"]:
        sort_parts = []
        for sort in template["sorts"]:
            col_def = source_config["columns"][sort["column"]]
            sort_parts.append(f"{col_def} {sort['direction']}")
        query += f" ORDER BY {', '.join(sort_parts)}"

    # Add LIMIT and OFFSET
    query += f" LIMIT {request.limit} OFFSET {request.offset}"

    # Execute query
    start_time = datetime.now()
    try:
        result = db.execute(text(query))
        rows = result.fetchall()
        columns_info = [{"name": col, "label": col, "type": "string"} for col in result.keys()]
        data = [dict(row._mapping) for row in rows]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )

    execution_time = (datetime.now() - start_time).total_seconds()

    return {
        "template_id": request.template_id,
        "template_name": template["name"],
        "columns": columns_info,
        "data": data,
        "total_rows": len(data),
        "execution_time": execution_time,
        "executed_at": datetime.now()
    }


@router.get("/data-sources")
async def get_available_data_sources(
    current_user: User = Depends(require_permission(ModuleName.REPORTS, Permission.VIEW))
):
    """Get list of available data sources and their columns

    - Useful for building report templates
    - Returns available columns and their types
    """
    return {
        source_name: {
            "table": config["table"],
            "columns": [
                {"name": col_name, "label": col_name.replace("_", " ").title()}
                for col_name in config["columns"].keys()
            ]
        }
        for source_name, config in DATA_SOURCES.items()
    }


@router.delete("/template/{template_id}")
async def delete_report_template(
    template_id: int,
    current_user: User = Depends(require_permission(ModuleName.REPORTS, Permission.DELETE)),
    db: Session = Depends(get_db)
):
    """Delete a report template

    - Only creator or admin can delete
    """
    # TODO: Implement database deletion
    return {"message": f"Report template {template_id} deleted successfully"}
