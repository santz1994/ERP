"""Pallet System Service
Business logic for pallet-based packing and validation
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.models.products import Product, ProductType
from app.core.models.warehouse import PurchaseOrder, PalletBarcode, PalletStatus, Location
from app.core.models.manufacturing import WorkOrder
from app.schemas.pallet import (
    PalletSpecsResponse,
    POPalletCalculationRequest,
    POPalletCalculationResponse,
    POPalletValidationRequest,
    POPalletValidationResponse,
    PackingPalletUpdateRequest,
    PackingPalletUpdateResponse,
    FGPalletReceiveRequest,
    FGPalletReceiveResponse,
    FGStockPalletDisplay,
    PalletBarcodeCreate,
    PalletBarcodeResponse,
)


class PalletService:
    """Service for pallet system operations"""

    def __init__(self, db: Session):
        self.db = db

    # ========================================================================
    # PALLET SPECIFICATIONS
    # ========================================================================

    def get_pallet_specs(self, product_id: int) -> PalletSpecsResponse:
        """Get pallet specifications for a product.
        
        Args:
            product_id: Product ID (must be Finish Good)
            
        Returns:
            PalletSpecsResponse with packing specifications
            
        Raises:
            HTTPException 404: Product not found
            HTTPException 400: Product is not a Finish Good
            HTTPException 400: Product has no pallet specs
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID {product_id} not found"
            )

        if product.type != ProductType.FINISH_GOOD:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.code} is not a Finish Good (type: {product.type.value})"
            )

        if not product.pcs_per_carton or not product.cartons_per_pallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product.code} has no pallet specifications. Please configure pcs_per_carton and cartons_per_pallet."
            )

        return PalletSpecsResponse(
            product_id=product.id,
            product_code=product.code,
            product_name=product.name,
            pcs_per_carton=product.pcs_per_carton,
            cartons_per_pallet=product.cartons_per_pallet,
            pcs_per_pallet=product.pcs_per_pallet
        )

    # ========================================================================
    # PO PALLET CALCULATION
    # ========================================================================

    def calculate_po_pallet_quantities(
        self, request: POPalletCalculationRequest
    ) -> POPalletCalculationResponse:
        """Calculate PO quantities based on pallet target.
        
        Business rule: PO quantity MUST be pallet multiples.
        
        Args:
            request: Contains article_id and target_pallets
            
        Returns:
            POPalletCalculationResponse with calculated quantities
            
        Example:
            Input: article_id=1 (AFTONSPARV), target_pallets=5
            Output: {
                expected_cartons: 40 (5 pallets × 8 cartons/pallet),
                calculated_pcs: 2400 (5 pallets × 480 pcs/pallet)
            }
        """
        # Get pallet specs
        pallet_specs = self.get_pallet_specs(request.article_id)

        # Calculate quantities
        expected_cartons = request.target_pallets * pallet_specs.cartons_per_pallet
        calculated_pcs = request.target_pallets * pallet_specs.pcs_per_pallet

        product = self.db.query(Product).filter(Product.id == request.article_id).first()

        return POPalletCalculationResponse(
            article_id=product.id,
            article_code=product.code,
            article_name=product.name,
            target_pallets=request.target_pallets,
            expected_cartons=expected_cartons,
            calculated_pcs=calculated_pcs,
            pallet_specs=pallet_specs
        )

    # ========================================================================
    # PO PALLET VALIDATION
    # ========================================================================

    def validate_po_pallet_quantity(
        self, request: POPalletValidationRequest
    ) -> POPalletValidationResponse:
        """Validate if PO quantity is a pallet multiple.
        
        Business rule: Warn if not pallet multiple, provide recommendations.
        
        Args:
            request: Contains article_id and quantity_pcs
            
        Returns:
            POPalletValidationResponse with validation result
            
        Example (valid):
            Input: article_id=1 (AFTONSPARV), quantity_pcs=2400
            Output: is_valid=True, pallets=5, remainder_pcs=0
            
        Example (invalid):
            Input: article_id=1 (AFTONSPARV), quantity_pcs=2500
            Output: is_valid=False, pallets=5, remainder_pcs=100,
                    recommendation="Adjust to 2400 pcs (5 pallets) or 2880 pcs (6 pallets)"
        """
        # Get pallet specs
        pallet_specs = self.get_pallet_specs(request.article_id)

        # Calculate breakdown
        pcs_per_pallet = pallet_specs.pcs_per_pallet
        pcs_per_carton = pallet_specs.pcs_per_carton

        complete_pallets = request.quantity_pcs // pcs_per_pallet
        remainder_after_pallets = request.quantity_pcs % pcs_per_pallet
        total_cartons = request.quantity_pcs // pcs_per_carton
        final_remainder = request.quantity_pcs % pcs_per_carton

        is_pallet_multiple = (remainder_after_pallets == 0)

        # Generate message and recommendation
        if is_pallet_multiple:
            message = f"✅ Valid pallet multiple: {request.quantity_pcs} pcs = {complete_pallets} pallet(s)"
            recommendation = None
        else:
            message = f"⚠️ Not a complete pallet multiple: {request.quantity_pcs} pcs = {complete_pallets} pallet(s) + {remainder_after_pallets} pcs loose"
            
            # Calculate nearest pallet multiples
            lower_qty = complete_pallets * pcs_per_pallet
            upper_qty = (complete_pallets + 1) * pcs_per_pallet
            recommendation = f"Adjust to {lower_qty} pcs ({complete_pallets} pallets) or {upper_qty} pcs ({complete_pallets + 1} pallets)"

        return POPalletValidationResponse(
            is_valid=is_pallet_multiple,
            is_pallet_multiple=is_pallet_multiple,
            quantity_pcs=request.quantity_pcs,
            pallets=complete_pallets,
            cartons=total_cartons,
            remainder_pcs=remainder_after_pallets,
            message=message,
            recommendation=recommendation,
            pallet_specs=pallet_specs
        )

    # ========================================================================
    # PACKING PALLET TRACKING
    # ========================================================================

    def update_packing_pallet_progress(
        self, request: PackingPalletUpdateRequest
    ) -> PackingPalletUpdateResponse:
        """Update packing progress with pallet formation tracking.
        
        Business rule: If validate_complete_pallets=True, system blocks partial pallets.
        
        Args:
            request: Contains work_order_id, cartons_packed, validate_complete_pallets
            
        Returns:
            PackingPalletUpdateResponse with validation result
            
        Raises:
            HTTPException 404: Work order not found
            HTTPException 400: Work order is not for Packing department
            HTTPException 400: Partial pallet detected (if validate_complete_pallets=True)
        """
        # Get work order
        wo = self.db.query(WorkOrder).filter(WorkOrder.id == request.work_order_id).first()
        if not wo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work Order ID {request.work_order_id} not found"
            )

        if wo.department.value != "Packing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Work Order {wo.wo_number} is not for Packing department (current: {wo.department.value})"
            )

        # Get product pallet specs
        pallet_specs = self.get_pallet_specs(wo.product_id)

        # Calculate pallets formed
        cartons_per_pallet = pallet_specs.cartons_per_pallet
        complete_pallets = request.cartons_packed // cartons_per_pallet
        remaining_cartons = request.cartons_packed % cartons_per_pallet

        is_complete = (remaining_cartons == 0)

        # Validate if required
        if request.validate_complete_pallets and not is_complete:
            error_msg = (
                f"Partial pallet detected: {request.cartons_packed} cartons = "
                f"{complete_pallets} pallet(s) + {remaining_cartons} carton(s) loose. "
                f"Expected multiple of {cartons_per_pallet} cartons."
            )
            return PackingPalletUpdateResponse(
                work_order_id=request.work_order_id,
                cartons_packed=request.cartons_packed,
                pallets_formed=complete_pallets,
                packing_validated=False,
                message=f"⚠️ {error_msg}",
                error=error_msg
            )

        # Update work order
        wo.cartons_packed = request.cartons_packed
        wo.pallets_formed = complete_pallets
        wo.packing_validated = is_complete

        self.db.commit()
        self.db.refresh(wo)

        message = (
            f"✅ Packed {request.cartons_packed} cartons → {complete_pallets} complete pallet(s)"
            if is_complete
            else f"⚠️ Packed {request.cartons_packed} cartons → {complete_pallets} pallet(s) + {remaining_cartons} carton(s) loose"
        )

        return PackingPalletUpdateResponse(
            work_order_id=request.work_order_id,
            cartons_packed=request.cartons_packed,
            pallets_formed=complete_pallets,
            packing_validated=is_complete,
            message=message,
            error=None
        )

    # ========================================================================
    # PALLET BARCODE MANAGEMENT
    # ========================================================================

    def generate_pallet_barcode(self) -> str:
        """Generate unique pallet barcode.
        
        Format: PLT-YYYY-XXXXX
        Example: PLT-2026-00001
        """
        current_year = datetime.now().year
        
        # Get last barcode for current year
        last_pallet = (
            self.db.query(PalletBarcode)
            .filter(PalletBarcode.barcode.like(f"PLT-{current_year}-%"))
            .order_by(PalletBarcode.id.desc())
            .first()
        )

        if last_pallet:
            # Extract sequence number
            last_seq = int(last_pallet.barcode.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"PLT-{current_year}-{new_seq:05d}"

    def create_pallet_barcode(
        self, request: PalletBarcodeCreate
    ) -> PalletBarcodeResponse:
        """Create new pallet barcode after packing.
        
        Business rule: Validate pallet content matches product specs.
        
        Args:
            request: Contains product_id, work_order_id, carton_count, total_pcs
            
        Returns:
            PalletBarcodeResponse with created barcode
            
        Raises:
            HTTPException 400: Pallet content doesn't match product specs
        """
        # Get pallet specs
        pallet_specs = self.get_pallet_specs(request.product_id)

        # Validate pallet content
        expected_pcs = request.carton_count * pallet_specs.pcs_per_carton
        if request.total_pcs != expected_pcs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Pallet content mismatch: {request.carton_count} cartons × "
                    f"{pallet_specs.pcs_per_carton} pcs/carton = {expected_pcs} pcs, "
                    f"but you entered {request.total_pcs} pcs"
                )
            )

        # Generate barcode
        barcode = self.generate_pallet_barcode()

        # Create pallet record
        pallet = PalletBarcode(
            barcode=barcode,
            product_id=request.product_id,
            work_order_id=request.work_order_id,
            carton_count=request.carton_count,
            total_pcs=request.total_pcs,
            status=PalletStatus.PACKED
        )

        self.db.add(pallet)
        self.db.commit()
        self.db.refresh(pallet)

        product = self.db.query(Product).filter(Product.id == request.product_id).first()

        return PalletBarcodeResponse(
            id=pallet.id,
            barcode=pallet.barcode,
            product_id=pallet.product_id,
            product_code=product.code,
            product_name=product.name,
            work_order_id=pallet.work_order_id,
            carton_count=pallet.carton_count,
            total_pcs=pallet.total_pcs,
            status=pallet.status.value,
            location_id=pallet.location_id,
            location_name=None,
            created_at=pallet.created_at,
            received_at=pallet.received_at,
            shipped_at=pallet.shipped_at
        )

    def receive_pallet_in_fg_warehouse(
        self, request: FGPalletReceiveRequest
    ) -> FGPalletReceiveResponse:
        """Receive pallet in FG warehouse by scanning barcode.
        
        Business rule: Update pallet status to RECEIVED and assign location.
        
        Args:
            request: Contains pallet_barcode, location_id, received_by_user_id
            
        Returns:
            FGPalletReceiveResponse with receive confirmation
            
        Raises:
            HTTPException 404: Pallet barcode not found
            HTTPException 400: Pallet already received
            HTTPException 404: Location not found
        """
        # Get pallet
        pallet = (
            self.db.query(PalletBarcode)
            .filter(PalletBarcode.barcode == request.pallet_barcode)
            .first()
        )
        if not pallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pallet barcode {request.pallet_barcode} not found"
            )

        if pallet.status != PalletStatus.PACKED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pallet {request.pallet_barcode} already {pallet.status.value}. Cannot receive again."
            )

        # Get location
        location = self.db.query(Location).filter(Location.id == request.location_id).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location ID {request.location_id} not found"
            )

        # Update pallet status
        pallet.status = PalletStatus.RECEIVED
        pallet.location_id = request.location_id
        pallet.received_at = datetime.now()

        self.db.commit()
        self.db.refresh(pallet)

        product = self.db.query(Product).filter(Product.id == pallet.product_id).first()

        return FGPalletReceiveResponse(
            pallet_barcode=pallet.barcode,
            status=pallet.status.value,
            product_code=product.code,
            product_name=product.name,
            carton_count=pallet.carton_count,
            total_pcs=pallet.total_pcs,
            location_name=location.name,
            received_at=pallet.received_at,
            message=f"✅ Received 1 pallet ({pallet.carton_count} cartons / {pallet.total_pcs} pcs)"
        )
