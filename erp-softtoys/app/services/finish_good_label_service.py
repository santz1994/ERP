"""Finish Good Label Service - IKEA Traceability Generator"""

from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, Department
from app.core.models.product import Product
from app.schemas.finish_good_label import (
    FinishGoodLabel,
    ProductInfo,
    POInfo,
    MOInfo,
    SPKWOInfo,
    FinishGoodLabelPrintRequest,
    FinishGoodLabelResponse
)


class FinishGoodLabelService:
    """Service untuk generate Finish Good Label dengan complete traceability"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_fg_labels(
        self,
        request: FinishGoodLabelPrintRequest
    ) -> FinishGoodLabelResponse:
        """Generate FG labels dengan traceability lengkap
        
        Args:
            request: Print request dengan MO ID dan carton info
            
        Returns:
            Response dengan list of labels dan QR codes
            
        Example:
            request = FinishGoodLabelPrintRequest(
                mo_id=123,
                carton_numbers=["CTN001", "CTN002", "CTN003"],
                qty_per_carton=[60, 60, 45]
            )
            result = await service.generate_fg_labels(request)
        """
        try:
            # 1. Load MO dengan complete relationships
            mo = await self._load_mo_with_traceability(request.mo_id)
            
            if not mo:
                return FinishGoodLabelResponse(
                    success=False,
                    message=f"Manufacturing Order ID {request.mo_id} not found"
                )
            
            # 2. Validate carton data
            if len(request.carton_numbers) != len(request.qty_per_carton):
                return FinishGoodLabelResponse(
                    success=False,
                    message="Carton numbers and quantities must have same length"
                )
            
            # 3. Generate labels untuk setiap carton
            labels: List[FinishGoodLabel] = []
            total_qty = sum(request.qty_per_carton)
            
            for idx, (carton_num, qty) in enumerate(zip(request.carton_numbers, request.qty_per_carton)):
                label = await self._create_label_for_carton(
                    mo=mo,
                    carton_number=carton_num,
                    qty_in_carton=qty,
                    total_qty=Decimal(str(total_qty)),
                    total_cartons=len(request.carton_numbers),
                    carton_index=idx + 1
                )
                labels.append(label)
            
            return FinishGoodLabelResponse(
                success=True,
                message=f"Generated {len(labels)} labels successfully",
                labels=labels,
                qr_codes=[]  # TODO: Generate actual QR codes
            )
            
        except Exception as e:
            return FinishGoodLabelResponse(
                success=False,
                message=f"Error generating labels: {str(e)}"
            )
    
    async def _load_mo_with_traceability(self, mo_id: int) -> Optional[ManufacturingOrder]:
        """Load MO dengan complete traceability (PO → MO → WO)"""
        
        query = (
            select(ManufacturingOrder)
            .where(ManufacturingOrder.id == mo_id)
            .options(
                selectinload(ManufacturingOrder.product),
                selectinload(ManufacturingOrder.work_orders)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _create_label_for_carton(
        self,
        mo: ManufacturingOrder,
        carton_number: str,
        qty_in_carton: int,
        total_qty: Decimal,
        total_cartons: int,
        carton_index: int
    ) -> FinishGoodLabel:
        """Create complete label untuk satu carton"""
        
        # Generate FG Barcode
        today = datetime.now()
        fg_barcode = f"FG-{today.year}-{mo.id:05d}-{carton_number}"
        
        # Product Information
        product_info = ProductInfo(
            product_code=mo.product.code,
            product_name=mo.product.name,
            product_category=mo.product.category,
            description=mo.product.description
        )
        
        # Work Orders Information (sorted by sequence)
        work_orders_info = []
        sorted_wos = sorted(mo.work_orders, key=lambda wo: wo.sequence or 0)
        
        for wo in sorted_wos:
            wo_info = SPKWOInfo(
                wo_number=wo.wo_number or f"WO-{wo.id}",
                department=wo.department.value,
                sequence=wo.sequence or 0,
                target_qty=wo.target_qty or Decimal('0'),
                actual_start_date=wo.actual_start_date,
                actual_completion_date=wo.actual_completion_date,
                production_date_stamp=wo.production_date_stamp,
                operator=None  # TODO: Get from worker_id relationship
            )
            work_orders_info.append(wo_info)
        
        # MO Information
        mo_info = MOInfo(
            mo_number=mo.batch_number,
            production_week=mo.production_week or "N/A",
            qty_planned=mo.qty_planned,
            qty_produced=mo.qty_produced,
            planned_production_date=mo.planned_production_date,
            actual_production_start_date=mo.actual_production_start_date,
            actual_production_end_date=mo.actual_production_end_date,
            label_production_date=mo.label_production_date or date.today(),
            destination_country=mo.destination_country,
            traceability_code=mo.traceability_code or f"{mo.batch_number}-{mo.production_week}",
            routing_type=mo.routing_type.value,
            work_orders=work_orders_info
        )
        
        # PO Information (if exists)
        po_info_list = []
        if mo.po_id:
            # TODO: Load actual PO data when PO model is ready
            po_info = POInfo(
                po_number=f"PO-{mo.po_id:05d}",  # Placeholder
                po_type="KAIN",  # Placeholder
                qty_ordered=mo.qty_planned,
                week=mo.production_week,
                destination=mo.destination_country,
                manufacturing_orders=[mo_info]
            )
            po_info_list.append(po_info)
        else:
            # No PO linked, create MO-only structure
            po_info = POInfo(
                po_number="N/A (Direct MO)",
                po_type="DIRECT",
                qty_ordered=mo.qty_planned,
                week=mo.production_week,
                destination=mo.destination_country,
                manufacturing_orders=[mo_info]
            )
            po_info_list.append(po_info)
        
        # Create complete label
        label = FinishGoodLabel(
            fg_barcode=fg_barcode,
            carton_number=carton_number,
            qty_in_carton=qty_in_carton,
            packing_date=date.today(),
            product=product_info,
            purchase_orders=po_info_list,
            total_qty=total_qty,
            total_cartons=total_cartons
        )
        
        return label
    
    async def get_label_by_barcode(self, barcode: str) -> Optional[FinishGoodLabel]:
        """Retrieve label information by FG barcode (for scanning/verification)"""
        
        # Parse barcode: FG-YYYY-MOID-CTNXXX
        parts = barcode.split('-')
        if len(parts) < 4 or parts[0] != 'FG':
            return None
        
        try:
            mo_id = int(parts[2])
            carton_num = parts[3]
            
            # Load MO
            mo = await self._load_mo_with_traceability(mo_id)
            if not mo:
                return None
            
            # Recreate label (qty_in_carton will be placeholder)
            label = await self._create_label_for_carton(
                mo=mo,
                carton_number=carton_num,
                qty_in_carton=0,  # Unknown from barcode alone
                total_qty=mo.qty_produced,
                total_cartons=1,  # Unknown
                carton_index=1
            )
            
            return label
            
        except (ValueError, IndexError):
            return None
    
    def format_label_for_print(self, label: FinishGoodLabel) -> str:
        """Format label untuk thermal printer (plain text)
        
        Returns:
            String formatted untuk printer thermal (80mm width)
        """
        
        lines = []
        lines.append("=" * 48)
        lines.append("QUTY KARUNIA - FINISH GOOD LABEL")
        lines.append("IKEA TRACEABILITY")
        lines.append("=" * 48)
        lines.append("")
        
        # Product Info
        lines.append("PRODUCT INFORMATION:")
        lines.append(f"  Code     : {label.product.product_code}")
        lines.append(f"  Name     : {label.product.product_name}")
        lines.append(f"  Category : {label.product.product_category}")
        lines.append("")
        
        # Carton Info
        lines.append("CARTON INFORMATION:")
        lines.append(f"  Barcode  : {label.fg_barcode}")
        lines.append(f"  Carton   : {label.carton_number}")
        lines.append(f"  Qty      : {label.qty_in_carton} pcs")
        lines.append(f"  Packed   : {label.packing_date}")
        lines.append(f"  Total    : {label.total_qty} pcs / {label.total_cartons} CTN")
        lines.append("")
        
        # Traceability Chain
        for po in label.purchase_orders:
            lines.append("-" * 48)
            lines.append(f"PO No {po.po_number} | QTY: {po.qty_ordered} pcs")
            lines.append(f"Type: {po.po_type} | Week: {po.week} | Dest: {po.destination}")
            
            for mo in po.manufacturing_orders:
                lines.append("")
                lines.append(f"  MO No {mo.mo_number} (Week {mo.production_week})")
                lines.append(f"  Qty: {mo.qty_produced}/{mo.qty_planned} pcs")
                lines.append(f"  Label Date: {mo.label_production_date}")
                lines.append(f"  Traceability: {mo.traceability_code}")
                lines.append(f"  Route: {mo.routing_type}")
                lines.append(f"  Destination: {mo.destination_country}")
                lines.append("")
                
                # Work Orders
                for wo in mo.work_orders:
                    status = "✓" if wo.actual_completion_date else "..."
                    lines.append(f"    {status} {wo.wo_number} - {wo.department}")
                    lines.append(f"       Seq: {wo.sequence} | Qty: {wo.target_qty} pcs")
                    if wo.actual_start_date:
                        lines.append(f"       Start: {wo.actual_start_date}")
                    if wo.actual_completion_date:
                        lines.append(f"       Done: {wo.actual_completion_date}")
                    if wo.production_date_stamp:
                        lines.append(f"       Stamp: {wo.production_date_stamp}")
        
        lines.append("")
        lines.append("=" * 48)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 48)
        
        return "\n".join(lines)
    
    def format_label_for_mobile(self, label: FinishGoodLabel) -> dict:
        """Format label untuk mobile app (JSON structure)"""
        
        return {
            "barcode": label.fg_barcode,
            "carton": label.carton_number,
            "qty": label.qty_in_carton,
            "product": {
                "code": label.product.product_code,
                "name": label.product.product_name
            },
            "traceability": [
                {
                    "po": po.po_number,
                    "week": po.week,
                    "mos": [
                        {
                            "mo": mo.mo_number,
                            "week": mo.production_week,
                            "qty": str(mo.qty_produced),
                            "trace_code": mo.traceability_code,
                            "departments": [
                                {
                                    "dept": wo.department,
                                    "wo": wo.wo_number,
                                    "completed": wo.actual_completion_date is not None
                                }
                                for wo in mo.work_orders
                            ]
                        }
                        for mo in po.manufacturing_orders
                    ]
                }
                for po in label.purchase_orders
            ]
        }
