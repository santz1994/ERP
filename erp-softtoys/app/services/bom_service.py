"""
BOM (Bill of Materials) Service
Feature #1: BOM Manufacturing Auto-Allocate Material
Session 35: Initial implementation

Handles:
- Material allocation from warehouse based on BOM Manufacturing
- Automatic material debt creation for shortages
- SPK creation with auto-allocation
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
import logging
from app.core.models.bom import BOMHeader, BOMDetail, BOMVariant, BOMType
from app.core.models.manufacturing import SPK, ManufacturingOrder, Department, SPKStatus
from app.core.models.warehouse import StockMove, StockMoveStatus, StockQuant
from app.core.models.products import Product
from app.core.models.users import User
from app.core.models.manufacturing import SPKMaterialAllocation
from app.core.models.production import SPKMaterialAllocationStatus

logger = logging.getLogger(__name__)

# Import material debt models (from Feature #4)
# from app.services.material_debt_service import MaterialDebtService


class BOMAllocationError(Exception):
    """BOM allocation specific error"""
    pass


class BOMService:
    """
    Service for BOM operations including material allocation
    
    Main Workflow:
    1. Get BOM Manufacturing for article
    2. Calculate material requirements
    3. Check warehouse stock
    4. Allocate available stock
    5. Create material debt for shortages
    6. Return allocation summary
    """

    def __init__(self):
        self.logger = logger

    async def allocate_material_for_spk(
        self,
        spk_id: int,
        mo_id: int,
        article_id: int,
        quantity: int,
        department: str,
        user_id: int,
        session: AsyncSession,
        allow_negative_inventory: bool = False,
    ) -> Dict[str, Any]:
        """
        Allocate material from warehouse for SPK based on BOM Manufacturing
        
        Returns:
        {
            "success": bool,
            "spk_id": int,
            "allocated_materials": [
                {
                    "material_id": int,
                    "material_name": str,
                    "qty_needed": Decimal,
                    "qty_allocated": Decimal,
                    "warehouse_location": str,
                    "status": "ALLOCATED" | "RESERVED" | "PENDING_DEBT"
                }
            ],
            "debt_materials": [
                {
                    "material_id": int,
                    "material_name": str,
                    "qty_shortage": Decimal,
                    "material_debt_id": int,
                    "debt_status": "PENDING_APPROVAL"
                }
            ],
            "summary": {
                "total_materials": int,
                "fully_allocated": int,
                "partially_allocated": int,
                "shortage_count": int
            }
        }
        
        Raises:
            BOMAllocationError: If allocation fails
        """
        try:
            self.logger.info(
                f"Starting material allocation for SPK {spk_id}, Article {article_id}, Qty {quantity}"
            )

            # 1. Get BOM Manufacturing for article
            bom = await self._get_bom_manufacturing(article_id, session)
            if not bom:
                raise BOMAllocationError(f"No BOM Manufacturing found for article {article_id}")

            # 2. Get BOM details (material lines)
            bom_details = await self._get_bom_details(bom.id, session)
            if not bom_details:
                self.logger.warning(f"BOM {bom.id} has no details")
                return {
                    "success": True,
                    "spk_id": spk_id,
                    "allocated_materials": [],
                    "debt_materials": [],
                    "summary": {
                        "total_materials": 0,
                        "fully_allocated": 0,
                        "partially_allocated": 0,
                        "shortage_count": 0,
                    }
                }

            # 3. Process each BOM detail line
            allocated_materials = []
            debt_materials = []
            allocation_count = 0
            shortage_count = 0

            for bom_detail in bom_details:
                # Calculate needed quantity
                qty_needed = Decimal(str(bom_detail.qty_needed)) * Decimal(str(quantity))
                
                # Add wastage
                if bom_detail.wastage_percent:
                    wastage = qty_needed * (Decimal(str(bom_detail.wastage_percent)) / Decimal(100))
                    qty_needed = qty_needed + wastage

                self.logger.debug(f"Material {bom_detail.component_id}: needed {qty_needed}")

                # 4. Check warehouse stock for this material
                stock_available = await self._get_available_stock(
                    bom_detail.component_id,
                    session
                )

                # 5. Allocate
                if stock_available >= qty_needed:
                    # Full allocation
                    allocation = await self._reserve_stock(
                        spk_id=spk_id,
                        material_id=bom_detail.component_id,
                        qty=qty_needed,
                        user_id=user_id,
                        session=session,
                        bom_line_id=bom_detail.id,
                        mo_id=mo_id,
                    )
                    
                    allocated_materials.append({
                        "material_id": bom_detail.component_id,
                        "material_name": bom_detail.component.name if hasattr(bom_detail, 'component') else f"Material {bom_detail.component_id}",
                        "qty_needed": float(qty_needed),
                        "qty_allocated": float(qty_needed),
                        "warehouse_location": "Primary",
                        "status": "ALLOCATED",
                        "spk_material_allocation_id": allocation.id,
                    })
                    allocation_count += 1

                elif stock_available > 0:
                    # Partial allocation
                    shortage = qty_needed - stock_available
                    
                    # Reserve what we have
                    allocation = await self._reserve_stock(
                        spk_id=spk_id,
                        material_id=bom_detail.component_id,
                        qty=stock_available,
                        user_id=user_id,
                        session=session,
                        bom_line_id=bom_detail.id,
                        mo_id=mo_id,
                        allocation_status=SPKMaterialAllocationStatus.PENDING_DEBT,
                    )

                    allocated_materials.append({
                        "material_id": bom_detail.component_id,
                        "material_name": bom_detail.component.name if hasattr(bom_detail, 'component') else f"Material {bom_detail.component_id}",
                        "qty_needed": float(qty_needed),
                        "qty_allocated": float(stock_available),
                        "warehouse_location": "Primary",
                        "status": "PENDING_DEBT",
                        "spk_material_allocation_id": allocation.id,
                    })

                    # Create material debt for shortage
                    if not allow_negative_inventory:
                        debt = await self._create_material_debt(
                            spk_id=spk_id,
                            material_id=bom_detail.component_id,
                            department=department,
                            qty_debt=shortage,
                            reason=f"Auto-allocated from BOM {bom.revision}, shortage due to insufficient stock",
                            user_id=user_id,
                            session=session,
                        )

                        debt_materials.append({
                            "material_id": bom_detail.component_id,
                            "material_name": bom_detail.component.name if hasattr(bom_detail, 'component') else f"Material {bom_detail.component_id}",
                            "qty_shortage": float(shortage),
                            "material_debt_id": debt.id if debt else None,
                            "debt_status": "PENDING_APPROVAL",
                        })
                        shortage_count += 1

                else:
                    # No stock available - create full debt
                    if not allow_negative_inventory:
                        debt = await self._create_material_debt(
                            spk_id=spk_id,
                            material_id=bom_detail.component_id,
                            department=department,
                            qty_debt=qty_needed,
                            reason=f"No stock available for {bom_detail.component_id}",
                            user_id=user_id,
                            session=session,
                        )

                        debt_materials.append({
                            "material_id": bom_detail.component_id,
                            "material_name": bom_detail.component.name if hasattr(bom_detail, 'component') else f"Material {bom_detail.component_id}",
                            "qty_shortage": float(qty_needed),
                            "material_debt_id": debt.id if debt else None,
                            "debt_status": "PENDING_APPROVAL",
                        })
                        shortage_count += 1

            # Summary
            summary = {
                "total_materials": len(bom_details),
                "fully_allocated": allocation_count,
                "partially_allocated": len([m for m in allocated_materials if m["status"] == "PENDING_DEBT"]),
                "shortage_count": shortage_count,
            }

            self.logger.info(
                f"Material allocation completed for SPK {spk_id}: "
                f"{allocation_count} fully allocated, {shortage_count} with shortages"
            )

            return {
                "success": True,
                "spk_id": spk_id,
                "allocated_materials": allocated_materials,
                "debt_materials": debt_materials,
                "summary": summary,
            }

        except Exception as e:
            self.logger.error(f"Error allocating materials for SPK {spk_id}: {str(e)}")
            raise BOMAllocationError(f"Failed to allocate materials: {str(e)}")

    async def _get_bom_manufacturing(
        self,
        article_id: int,
        session: AsyncSession,
    ) -> Optional[BOMHeader]:
        """Get BOM Manufacturing for article"""
        try:
            query = select(BOMHeader).where(
                and_(
                    BOMHeader.product_id == article_id,
                    BOMHeader.bom_type == BOMType.MANUFACTURING,
                    BOMHeader.is_active == True,
                )
            ).order_by(BOMHeader.revision.desc())

            result = await session.execute(query)
            return result.scalars().first()
        except Exception as e:
            self.logger.error(f"Error fetching BOM for article {article_id}: {str(e)}")
            return None

    async def _get_bom_details(
        self,
        bom_header_id: int,
        session: AsyncSession,
    ) -> List[BOMDetail]:
        """Get BOM detail lines"""
        try:
            query = select(BOMDetail).where(
                BOMDetail.bom_header_id == bom_header_id
            ).options(
                joinedload(BOMDetail.component)
            )

            result = await session.execute(query)
            return result.scalars().unique().all()
        except Exception as e:
            self.logger.error(f"Error fetching BOM details for header {bom_header_id}: {str(e)}")
            return []

    async def _get_available_stock(
        self,
        material_id: int,
        session: AsyncSession,
    ) -> Decimal:
        """Get available stock quantity for material"""
        try:
            # Query StockQuant to get available qty for the material
            query = select(StockQuant).where(
                StockQuant.product_id == material_id
            )
            
            result = await session.execute(query)
            stock_quants = result.scalars().all()
            
            # Sum available qty from all locations
            total_available = Decimal(0)
            for quant in stock_quants:
                available = Decimal(str(quant.qty_on_hand)) - Decimal(str(quant.qty_reserved))
                if available > 0:
                    total_available += available
            
            return total_available
        except Exception as e:
            self.logger.warning(f"Error getting stock for material {material_id}: {str(e)}")
            return Decimal(0)

    async def _reserve_stock(
        self,
        spk_id: int,
        material_id: int,
        qty: Decimal,
        user_id: int,
        session: AsyncSession,
        bom_line_id: Optional[int] = None,
        mo_id: Optional[int] = None,
        allocation_status: str = SPKMaterialAllocationStatus.ALLOCATED,
    ) -> SPKMaterialAllocation:
        """Create stock reservation and allocation record"""
        try:
            allocation = SPKMaterialAllocation(
                spk_id=spk_id,
                material_id=material_id,
                mo_id=mo_id,
                qty_needed=qty,
                qty_allocated=qty,
                qty_from_debt=Decimal(0),
                allocation_status=allocation_status,
                has_material_debt=allocation_status == SPKMaterialAllocationStatus.PENDING_DEBT,
                allocated_by_id=user_id,
                allocated_at=datetime.utcnow(),
                bom_line_id=bom_line_id,
            )

            session.add(allocation)
            await session.flush()  # Get the ID without committing
            
            self.logger.debug(
                f"Created allocation {allocation.id}: SPK {spk_id}, Material {material_id}, Qty {qty}"
            )

            return allocation

        except Exception as e:
            self.logger.error(f"Error reserving stock: {str(e)}")
            raise

    async def _create_material_debt(
        self,
        spk_id: int,
        material_id: int,
        department: str,
        qty_debt: Decimal,
        reason: str,
        user_id: int,
        session: AsyncSession,
    ) -> Optional[Any]:
        """
        Create material debt record
        TODO: Integrate with MaterialDebtService from Feature #4
        """
        try:
            self.logger.info(
                f"Creating material debt: SPK {spk_id}, Material {material_id}, "
                f"Qty {qty_debt}, Department {department}"
            )

            # Placeholder - will be properly implemented in Feature #4
            # For now just log the debt creation
            
            return None

        except Exception as e:
            self.logger.error(f"Error creating material debt: {str(e)}")
            return None
