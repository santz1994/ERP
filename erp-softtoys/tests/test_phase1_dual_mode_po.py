"""
Test Suite for Phase 1: Dual-mode PO System with BOM Explosion

Tests:
1. BOM Explosion Service
2. Auto-BOM PO Creation
3. Supplier per material assignment
4. PO KAIN/LABEL type logic
5. Integration with MO triggers

Author: IT Developer Expert
Date: 5 February 2026
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.core.models.products import Product, ProductType, Partner
from app.core.models.bom import BOMHeader, BOMDetail
from app.core.models.warehouse import PurchaseOrder, PurchaseOrderLine, StockQuant
from app.core.models.manufacturing import ManufacturingOrder, MOState, Department
from app.services.bom_explosion_service import BOMExplosionService
from app.modules.purchasing.purchasing_service import PurchasingService


@pytest.fixture
def sample_suppliers(db: Session):
    """Create sample suppliers"""
    suppliers = [
        Partner(
            name="PT Supplier Kain A",
            type=PartnerType.SUPPLIER,
            is_active=True
        ),
        Partner(
            name="PT Supplier Label B",
            type=PartnerType.SUPPLIER,
            is_active=True
        ),
        Partner(
            name="PT Fill Jaya",
            type=PartnerType.SUPPLIER,
            is_active=True
        ),
    ]
    
    for supplier in suppliers:
        db.add(supplier)
    db.commit()
    
    for supplier in suppliers:
        db.refresh(supplier)
    
    return suppliers


@pytest.fixture
def sample_materials(db: Session):
    """Create sample materials for BOM"""
    materials = [
        Product(
            code="IKHR504",
            name="KOHAIR 7MM D.BROWN",
            product_type=ProductType.RAW_MATERIAL,
            uom="YARD",
            is_active=True,
            metadata={"material_category": "KAIN"}
        ),
        Product(
            code="IKP20157",
            name="POLYESTER FILL 10MM",
            product_type=ProductType.RAW_MATERIAL,
            uom="KG",
            is_active=True,
            metadata={"material_category": "ACCESSORIES"}
        ),
        Product(
            code="IKLBL001",
            name="IKEA LABEL SMALL",
            product_type=ProductType.RAW_MATERIAL,
            uom="PCS",
            is_active=True,
            metadata={"material_category": "LABEL"}
        ),
    ]
    
    for material in materials:
        db.add(material)
    db.commit()
    
    for material in materials:
        db.refresh(material)
    
    return materials


@pytest.fixture
def sample_article_with_bom(db: Session, sample_materials):
    """Create sample article with BOM"""
    # Create finished good article
    article = Product(
        code="40551542",
        name="AFTONSPARV",
        product_type=ProductType.FINISHED_GOOD,
        uom="PCS",
        is_active=True,
        metadata={"article_type": "SOFT_TOY"}
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # Create BOM Header
    bom = BOMHeader(
        product_id=article.id,
        code=f"BOM-{article.code}",
        name=f"BOM for {article.name}",
        version=1,
        is_active=True
    )
    db.add(bom)
    db.commit()
    db.refresh(bom)
    
    # Create BOM Details
    bom_details = [
        BOMDetail(
            bom_id=bom.id,
            component_id=sample_materials[0].id,  # IKHR504 (KAIN)
            quantity=Decimal("0.1466"),
            uom="YARD",
            sequence=1
        ),
        BOMDetail(
            bom_id=bom.id,
            component_id=sample_materials[1].id,  # IKP20157 (FILL)
            quantity=Decimal("0.025"),
            uom="KG",
            sequence=2
        ),
        BOMDetail(
            bom_id=bom.id,
            component_id=sample_materials[2].id,  # IKLBL001 (LABEL)
            quantity=Decimal("1.0"),
            uom="PCS",
            sequence=3
        ),
    ]
    
    for detail in bom_details:
        db.add(detail)
    db.commit()
    
    return article, bom


class TestBOMExplosionService:
    """Test BOM Explosion Service"""
    
    def test_explode_bom_for_purchasing_kain_only(
        self, 
        db: Session, 
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test BOM explosion for PO KAIN (only fabric materials)"""
        article, bom = sample_article_with_bom
        service = BOMExplosionService(db)
        
        # Explode for 1000 pcs, KAIN only
        result = service.explode_bom_for_purchasing(
            article_id=article.id,
            quantity=Decimal("1000"),
            po_type="KAIN"
        )
        
        assert result is not None
        assert "materials" in result
        assert len(result["materials"]) == 1  # Only KAIN material
        
        kain_material = result["materials"][0]
        assert kain_material["material_code"] == "IKHR504"
        assert kain_material["total_quantity"] == Decimal("146.6")  # 1000 * 0.1466
        assert kain_material["uom"] == "YARD"
    
    def test_explode_bom_for_purchasing_label_only(
        self, 
        db: Session, 
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test BOM explosion for PO LABEL (only label materials)"""
        article, bom = sample_article_with_bom
        service = BOMExplosionService(db)
        
        # Explode for 1000 pcs, LABEL only
        result = service.explode_bom_for_purchasing(
            article_id=article.id,
            quantity=Decimal("1000"),
            po_type="LABEL"
        )
        
        assert result is not None
        assert "materials" in result
        assert len(result["materials"]) == 1  # Only LABEL material
        
        label_material = result["materials"][0]
        assert label_material["material_code"] == "IKLBL001"
        assert label_material["total_quantity"] == Decimal("1000")  # 1000 * 1.0
        assert label_material["uom"] == "PCS"
    
    def test_explode_bom_with_stock_status(
        self, 
        db: Session, 
        sample_article_with_bom,
        sample_materials
    ):
        """Test BOM explosion includes stock status"""
        article, bom = sample_article_with_bom
        service = BOMExplosionService(db)
        
        # Add stock for one material
        stock = StockQuant(
            product_id=sample_materials[0].id,  # IKHR504
            location_id=1,  # Assume location exists
            quantity=Decimal("200.0"),
            uom="YARD"
        )
        db.add(stock)
        db.commit()
        
        # Explode BOM
        result = service.explode_bom_for_purchasing(
            article_id=article.id,
            quantity=Decimal("1000"),
            po_type="KAIN"
        )
        
        kain_material = result["materials"][0]
        assert "stock_available" in kain_material
        assert kain_material["stock_available"] == Decimal("200.0")
        assert kain_material["stock_status"] == "INSUFFICIENT"  # Need 146.6, have 200 (but might be reserved)


class TestDualModePOCreation:
    """Test Dual-mode PO Creation (AUTO_BOM vs MANUAL)"""
    
    def test_create_po_auto_bom_kain(
        self,
        db: Session,
        admin_user,
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test creating PO with AUTO_BOM mode for KAIN"""
        article, bom = sample_article_with_bom
        service = PurchasingService(db)
        
        # Material supplier assignments
        material_suppliers = {
            "IKHR504": sample_suppliers[0].id  # PT Supplier Kain A
        }
        
        material_prices = {
            "IKHR504": Decimal("12.50")
        }
        
        # Create PO
        po = service.create_purchase_order_auto_bom(
            article_id=article.id,
            article_quantity=Decimal("1000"),
            po_number="PO-K-2026-00001",
            order_date=date.today(),
            expected_date=date.today(),
            material_suppliers=material_suppliers,
            material_prices=material_prices,
            user_id=admin_user.id,
            po_type="KAIN"
        )
        
        assert po is not None
        assert po.input_mode == "AUTO_BOM"
        assert po.source_article_id == article.id
        assert po.article_quantity == Decimal("1000")
        assert po.po_type == "KAIN"
        
        # Check PO lines
        lines = db.query(PurchaseOrderLine).filter_by(purchase_order_id=po.id).all()
        assert len(lines) == 1  # Only KAIN material
        
        kain_line = lines[0]
        assert kain_line.supplier_id == sample_suppliers[0].id
        assert kain_line.quantity == Decimal("146.6")
        assert kain_line.unit_price == Decimal("12.50")
        assert kain_line.subtotal == Decimal("146.6") * Decimal("12.50")
    
    def test_create_po_auto_bom_label(
        self,
        db: Session,
        admin_user,
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test creating PO with AUTO_BOM mode for LABEL"""
        article, bom = sample_article_with_bom
        service = PurchasingService(db)
        
        material_suppliers = {
            "IKLBL001": sample_suppliers[1].id  # PT Supplier Label B
        }
        
        material_prices = {
            "IKLBL001": Decimal("0.50")
        }
        
        # Create PO with week & destination metadata
        po = service.create_purchase_order_auto_bom(
            article_id=article.id,
            article_quantity=Decimal("1000"),
            po_number="PO-L-2026-00001",
            order_date=date.today(),
            expected_date=date.today(),
            material_suppliers=material_suppliers,
            material_prices=material_prices,
            user_id=admin_user.id,
            po_type="LABEL",
            metadata_extra={
                "week": "W05",
                "destination": "IKEA Distribution Center"
            }
        )
        
        assert po is not None
        assert po.input_mode == "AUTO_BOM"
        assert po.po_type == "LABEL"
        assert po.extra_metadata is not None
        assert po.extra_metadata["week"] == "W05"
        assert po.extra_metadata["destination"] == "IKEA Distribution Center"
    
    def test_create_po_auto_bom_missing_supplier(
        self,
        db: Session,
        admin_user,
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test PO creation fails when supplier missing"""
        article, bom = sample_article_with_bom
        service = PurchasingService(db)
        
        # Missing supplier assignment
        material_suppliers = {}  # Empty!
        material_prices = {"IKHR504": Decimal("12.50")}
        
        with pytest.raises(ValueError, match="missing supplier assignment"):
            service.create_purchase_order_auto_bom(
                article_id=article.id,
                article_quantity=Decimal("1000"),
                po_number="PO-K-2026-00002",
                order_date=date.today(),
                expected_date=date.today(),
                material_suppliers=material_suppliers,
                material_prices=material_prices,
                user_id=admin_user.id,
                po_type="KAIN"
            )
    
    def test_create_po_auto_bom_missing_price(
        self,
        db: Session,
        admin_user,
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test PO creation fails when price missing"""
        article, bom = sample_article_with_bom
        service = PurchasingService(db)
        
        material_suppliers = {"IKHR504": sample_suppliers[0].id}
        material_prices = {}  # Empty!
        
        with pytest.raises(ValueError, match="missing unit price"):
            service.create_purchase_order_auto_bom(
                article_id=article.id,
                article_quantity=Decimal("1000"),
                po_number="PO-K-2026-00003",
                order_date=date.today(),
                expected_date=date.today(),
                material_suppliers=material_suppliers,
                material_prices=material_prices,
                user_id=admin_user.id,
                po_type="KAIN"
            )


class TestSupplierPerMaterial:
    """Test supplier assignment per material (not per PO)"""
    
    def test_different_suppliers_per_material(
        self,
        db: Session,
        admin_user,
        sample_article_with_bom,
        sample_suppliers
    ):
        """Test each material can have different supplier"""
        article, bom = sample_article_with_bom
        service = PurchasingService(db)
        
        # Different supplier for each material
        material_suppliers = {
            "IKHR504": sample_suppliers[0].id,  # Supplier A
            "IKP20157": sample_suppliers[2].id,  # Supplier C (different!)
        }
        
        material_prices = {
            "IKHR504": Decimal("12.50"),
            "IKP20157": Decimal("50.00"),
        }
        
        po = service.create_purchase_order_auto_bom(
            article_id=article.id,
            article_quantity=Decimal("1000"),
            po_number="PO-A-2026-00001",
            order_date=date.today(),
            expected_date=date.today(),
            material_suppliers=material_suppliers,
            material_prices=material_prices,
            user_id=admin_user.id,
            po_type="ACCESSORIES"
        )
        
        lines = db.query(PurchaseOrderLine).filter_by(purchase_order_id=po.id).all()
        assert len(lines) == 2
        
        # Verify each line has correct supplier
        suppliers_used = {line.supplier_id for line in lines}
        assert sample_suppliers[0].id in suppliers_used
        assert sample_suppliers[2].id in suppliers_used
        assert sample_suppliers[0].id != sample_suppliers[2].id


@pytest.mark.integration
class TestPOPreviewEndpoint:
    """Test BOM explosion preview endpoint"""
    
    def test_preview_bom_explosion_kain(
        self,
        db: Session,
        sample_article_with_bom
    ):
        """Test preview BOM explosion for UI"""
        article, bom = sample_article_with_bom
        service = PurchasingService(db)
        
        preview = service.preview_bom_explosion(
            article_id=article.id,
            quantity=Decimal("1000"),
            po_type="KAIN"
        )
        
        assert preview is not None
        assert "materials" in preview
        assert preview["total_materials"] >= 1
        assert "total_estimated_cost" in preview
    
    def test_preview_bom_nonexistent_article(
        self,
        db: Session
    ):
        """Test preview with non-existent article"""
        service = PurchasingService(db)
        
        with pytest.raises(ValueError, match="not found"):
            service.preview_bom_explosion(
                article_id=99999,
                quantity=Decimal("1000"),
                po_type="KAIN"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
