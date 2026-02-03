"""
BOM Explosion Service - Multi-level BOM expansion and Work Order generation

Author: IT Developer Expert
Date: 3 Februari 2026
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.models.products import Product
from app.core.models.bom import BOMHeader, BOMDetail
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, Department, WorkOrderStatus
from app.core.models.warehouse import StockQuant


class BOMExplosionService:
    """Service for exploding multi-level BOMs and generating Work Orders"""
    
    def __init__(self, db: Session):
        self.db = db
        self.explosion_cache = {}  # Cache to avoid re-exploding same BOM
    
    def explode_mo_and_generate_work_orders(
        self, 
        mo_id: int,
        qty_planned: Decimal
    ) -> List[WorkOrder]:
        """
        Main entry point: Explode BOM for Finished Good and generate Work Orders
        
        Args:
            mo_id: Manufacturing Order ID
            qty_planned: Quantity to produce
        
        Returns:
            List of generated Work Orders (one per department)
        """
        
        # Get MO
        mo = self.db.query(ManufacturingOrder).filter_by(id=mo_id).first()
        if not mo:
            raise ValueError(f"Manufacturing Order {mo_id} not found")
        
        # Get Finished Good product
        fg_product = self.db.query(Product).filter_by(id=mo.product_id).first()
        if not fg_product:
            raise ValueError(f"Product {mo.product_id} not found")
        
        print(f"\n{'='*80}")
        print(f"🎯 EXPLODING BOM FOR MO: {mo.batch_number}")
        print(f"📦 Finished Good: {fg_product.code} - {fg_product.name}")
        print(f"🎯 Target Quantity: {qty_planned} pcs")
        print("="*80)
        
        # Explode BOM multi-level
        explosion_result = self.explode_bom_multi_level(
            product_id=fg_product.id,
            qty_required=qty_planned,
            level=0
        )
        
        # Generate Work Orders from explosion result
        work_orders = self._generate_work_orders_from_explosion(
            mo=mo,
            explosion_result=explosion_result,
            qty_planned=qty_planned
        )
        
        # Update MO status
        mo.bom_explosion_complete = True
        mo.total_departments = len(work_orders)
        self.db.commit()
        
        print(f"\n✅ Generated {len(work_orders)} Work Orders for MO {mo.batch_number}")
        
        return work_orders
    
    def explode_bom_multi_level(
        self,
        product_id: int,
        qty_required: Decimal,
        level: int = 0,
        max_level: int = 10
    ) -> Dict:
        """
        Recursively explode BOM from Finished Good down to raw materials
        
        Args:
            product_id: Product to explode
            qty_required: Quantity needed
            level: Current recursion level (for indentation)
            max_level: Maximum recursion depth (safety)
        
        Returns:
            Dict with explosion results including all WIP stages and materials
        """
        
        indent = "  " * level
        
        # Safety check
        if level > max_level:
            print(f"{indent}⚠️  Max recursion level reached!")
            return {}
        
        # Get product
        product = self.db.query(Product).filter_by(id=product_id).first()
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        print(f"{indent}{'🔍' if level > 0 else '🎯'} Level {level}: {product.code} x {qty_required}")
        
        # Check cache
        cache_key = f"{product_id}_{qty_required}"
        if cache_key in self.explosion_cache:
            print(f"{indent}  💾 Using cached result")
            return self.explosion_cache[cache_key]
        
        # Get BOM for this product
        bom = self.db.query(BOMHeader).filter_by(
            product_id=product_id,
            is_active=True
        ).first()
        
        if not bom:
            # No BOM = raw material or purchased item
            print(f"{indent}  ✅ Raw material/Purchased (no BOM)")
            result = {
                'product_id': product_id,
                'product_code': product.code,
                'product_name': product.name,
                'product_type': getattr(product, 'product_type', 'raw_material'),
                'qty_required': qty_required,
                'level': level,
                'is_leaf': True,  # Terminal node
                'materials': [],
                'children': []
            }
            self.explosion_cache[cache_key] = result
            return result
        
        # BOM exists - explode details
        print(f"{indent}  📋 BOM found: {bom.id} ({len(bom.details)} components)")
        
        materials = []
        children = []
        
        for detail in bom.details:
            component = detail.component
            qty_needed_per_unit = detail.qty_needed
            total_qty_needed = qty_needed_per_unit * qty_required
            
            print(f"{indent}    - {component.code}: {qty_needed_per_unit} x {qty_required} = {total_qty_needed}")
            
            # Check if component is WIP (needs further explosion) or raw material
            component_type = getattr(component, 'product_type', 'raw_material')
            
            if component_type == 'wip' or '_WIP_' in component.code.upper():
                # WIP product - needs recursive explosion
                print(f"{indent}      🔄 WIP detected - exploding...")
                child_explosion = self.explode_bom_multi_level(
                    product_id=component.id,
                    qty_required=total_qty_needed,
                    level=level + 1,
                    max_level=max_level
                )
                children.append(child_explosion)
            else:
                # Raw material - terminal node
                materials.append({
                    'component_id': component.id,
                    'component_code': component.code,
                    'component_name': component.name,
                    'qty_per_unit': qty_needed_per_unit,
                    'total_qty_needed': total_qty_needed,
                    'uom': 'PCE',  # TODO: Get from product
                    'wastage_percent': detail.wastage_percent
                })
        
        # Build result
        result = {
            'product_id': product_id,
            'product_code': product.code,
            'product_name': product.name,
            'product_type': getattr(product, 'product_type', 'wip'),
            'qty_required': qty_required,
            'level': level,
            'bom_id': bom.id,
            'department': self._detect_department_from_product_code(product.code),
            'is_leaf': len(children) == 0,
            'materials': materials,
            'children': children
        }
        
        # Cache result
        self.explosion_cache[cache_key] = result
        
        return result
    
    def _generate_work_orders_from_explosion(
        self,
        mo: ManufacturingOrder,
        explosion_result: Dict,
        qty_planned: Decimal
    ) -> List[WorkOrder]:
        """
        Generate Work Orders from explosion result
        
        Strategy:
        - Walk through explosion tree
        - Create one WO per unique department found
        - Set dependencies (WO sequence based on BOM levels)
        """
        
        print(f"\n{'='*80}")
        print("🏭 GENERATING WORK ORDERS")
        print("="*80)
        
        # Collect all WIP stages with their departments
        wip_stages = self._collect_wip_stages(explosion_result)
        
        # Sort by level (deeper levels first = earlier departments)
        wip_stages_sorted = sorted(wip_stages, key=lambda x: x['level'], reverse=True)
        
        print(f"\n📊 Found {len(wip_stages_sorted)} WIP stages:")
        for idx, stage in enumerate(wip_stages_sorted, 1):
            print(f"  {idx}. Level {stage['level']}: {stage['department']} → {stage['product_code']} ({stage['qty_required']} pcs)")
        
        # Generate Work Orders
        work_orders = []
        
        for sequence, stage in enumerate(wip_stages_sorted, 1):
            # Calculate buffer (different per department)
            buffer_percent = self._get_department_buffer_percent(stage['department'])
            target_qty = stage['qty_required'] * (1 + buffer_percent / 100)
            
            # Determine input WIP (from previous stage)
            input_wip_product_id = None
            if sequence > 1:
                prev_stage = wip_stages_sorted[sequence - 2]
                input_wip_product_id = prev_stage['product_id']
            
            # Detect if this is subcon department (EMBROIDERY uses outsourcing)
            is_subcon = stage['department'] == 'EMBROIDERY'
            subcon_note = " [SUBCON - Outsourced to embroidery vendor]" if is_subcon else ""
            
            # Create Work Order
            wo = WorkOrder(
                mo_id=mo.id,
                product_id=stage['product_id'],  # Output WIP product
                wo_number=self._generate_wo_number(mo.batch_number, stage['department'], sequence),
                department=stage['department'],
                sequence=sequence,
                input_wip_product_id=input_wip_product_id,
                output_wip_product_id=stage['product_id'],
                target_qty=target_qty,
                status='PENDING' if sequence > 1 else 'PENDING',  # All start as PENDING
                input_qty=stage['qty_required'],  # Set input_qty as required field
                notes=f"Auto-generated from BOM explosion (Level {stage['level']}){subcon_note}"
            )
            
            self.db.add(wo)
            self.db.flush()  # Get ID
            
            # Allocate materials for this WO
            self._allocate_materials_to_wo(wo, stage)
            
            work_orders.append(wo)
            
            print(f"  ✅ Created WO: {wo.wo_number} ({stage['department']}) - Target: {target_qty} pcs")
        
        self.db.commit()
        
        return work_orders
    
    def _collect_wip_stages(self, explosion_result: Dict, stages: List = None) -> List[Dict]:
        """Recursively collect all WIP stages from explosion tree"""
        
        if stages is None:
            stages = []
        
        # Add current stage if it's WIP (exclude finished goods)
        product_type = explosion_result.get('product_type', '')
        product_code = explosion_result.get('product_code', '')
        department = explosion_result.get('department', 'UNKNOWN')
        
        # Only include if it's explicitly a WIP product (not finished goods or raw materials)
        is_wip = product_type == 'wip' or '_WIP_' in product_code.upper()
        has_valid_department = department != 'UNKNOWN' and department != 'N/A'
        
        if is_wip and has_valid_department:
            stages.append({
                'product_id': explosion_result['product_id'],
                'product_code': explosion_result['product_code'],
                'product_name': explosion_result['product_name'],
                'qty_required': explosion_result['qty_required'],
                'level': explosion_result['level'],
                'department': department,
                'materials': explosion_result.get('materials', [])
            })
        
        # Recursively collect from children
        for child in explosion_result.get('children', []):
            self._collect_wip_stages(child, stages)
        
        return stages
    
    def _detect_department_from_product_code(self, product_code: str) -> str:
        """Detect department from WIP product code"""
        
        code_upper = product_code.upper()
        
        if 'WIP_CUTTING' in code_upper or '_CUTTING' in code_upper:
            return 'CUTTING'
        elif 'WIP_EMBO' in code_upper or '_EMBO' in code_upper or 'EMBO' in code_upper:
            # EMBROIDERY (often uses subcon/outsourcing)
            return 'EMBROIDERY'
        elif 'WIP_SEWING' in code_upper or 'WIP_SKIN' in code_upper or 'WIP_BAJU' in code_upper or '_SKIN' in code_upper:
            return 'SEWING'
        elif 'WIP_FINISHING' in code_upper or 'WIP_BONEKA' in code_upper or '_BONEKA' in code_upper or '_STUFFED' in code_upper:
            return 'FINISHING'
        elif 'WIP_PACKING' in code_upper or '_PACKING' in code_upper:
            return 'PACKING'
        else:
            # Last resort: check for common patterns
            if 'EMBR' in code_upper:  # EMBROIDERED, etc.
                return 'EMBROIDERY'
            return 'UNKNOWN'
    
    def _get_department_buffer_percent(self, department: str) -> Decimal:
        """Get buffer percentage per department"""
        
        buffers = {
            'CUTTING': Decimal('10.0'),      # +10%
            'EMBROIDERY': Decimal('7.0'),    # +7%
            'SEWING': Decimal('6.7'),        # +6.7%
            'FINISHING': Decimal('4.4'),     # +4.4%
            'PACKING': Decimal('3.3'),       # +3.3%
        }
        
        return buffers.get(department, Decimal('5.0'))  # Default 5%
    
    def _generate_wo_number(self, mo_number: str, department: str, sequence: int) -> str:
        """Generate Work Order number"""
        
        dept_code = {
            'CUTTING': 'CUT',
            'EMBROIDERY': 'EMB',  # Subcon department
            'SEWING': 'SEW',
            'FINISHING': 'FIN',
            'PACKING': 'PCK',
            'UNKNOWN': 'UNK'  # Fallback
        }.get(department, 'WO')
        
        # Format: MO-2026-00089-CUT-01
        return f"{mo_number}-{dept_code}-{sequence:02d}"
    
    def _allocate_materials_to_wo(self, wo: WorkOrder, stage: Dict):
        """Allocate materials to Work Order (placeholder for now)"""
        
        # TODO: Implement material allocation
        # This will create SPKMaterialAllocation records
        
        materials = stage.get('materials', [])
        print(f"    📦 Allocating {len(materials)} materials to WO {wo.wo_number}")
        
        # For now, just log
        for material in materials:
            print(f"      - {material['component_code']}: {material['total_qty_needed']}")
    
    def check_wo_dependencies(self, wo_id: int) -> Tuple[bool, str]:
        """
        Check if Work Order can start (dependencies satisfied)
        
        Returns:
            (can_start: bool, reason: str)
        """
        
        wo = self.db.query(WorkOrder).filter_by(id=wo_id).first()
        if not wo:
            return False, "Work Order not found"
        
        # Check 1: First WO in sequence? Always ready
        if wo.sequence == 1:
            return True, "First department - ready to start"
        
        # Check 2: Previous WO completed?
        prev_wo = self.db.query(WorkOrder).filter_by(
            mo_id=wo.mo_id,
            sequence=wo.sequence - 1
        ).first()
        
        if not prev_wo:
            return False, "Previous Work Order not found"
        
        if prev_wo.status != WorkOrderStatus.FINISHED:
            return False, f"Waiting for {prev_wo.department} to complete (currently: {prev_wo.status})"
        
        # Check 3: Input WIP available in warehouse?
        if wo.input_wip_product_id:
            stock = self.db.query(StockQuant).filter_by(
                product_id=wo.input_wip_product_id
            ).first()
            
            available_qty = stock.quantity if stock else Decimal('0')
            
            if available_qty < wo.target_qty:
                return False, f"Insufficient WIP stock: {available_qty}/{wo.target_qty} pcs"
        
        return True, "All dependencies satisfied - ready to start"
    
    def update_wo_status_auto(self, mo_id: int):
        """
        Auto-update Work Order statuses based on dependencies
        Called after WO completion to unlock next WOs
        """
        
        work_orders = self.db.query(WorkOrder).filter_by(
            mo_id=mo_id,
            status=WorkOrderStatus.PENDING
        ).order_by(WorkOrder.sequence).all()
        
        for wo in work_orders:
            can_start, reason = self.check_wo_dependencies(wo.id)
            
            if can_start:
                wo.status = WorkOrderStatus.RUNNING
                print(f"  🔓 WO {wo.wo_number} is now RUNNING: {reason}")
            else:
                print(f"  🔒 WO {wo.wo_number} still PENDING: {reason}")
        
        self.db.commit()
