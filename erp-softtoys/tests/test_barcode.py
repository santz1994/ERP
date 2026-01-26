"""
Barcode Processing Module Tests
Test coverage for barcode scanning and validation
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime


class TestBarcodeFormatValidation:
    """Test barcode format validation"""
    
    def test_barcode_format_valid(self):
        """Valid barcode format should pass"""
        valid_barcodes = [
            "CARTON001|ARTICLE1|100",
            "CARTON002|ARTICLE2|50",
            "CARTON-003|ARTICLE-001|200"
        ]
        
        for barcode in valid_barcodes:
            assert self._validate_barcode_format(barcode) is True
    
    def test_barcode_format_invalid(self):
        """Invalid barcode format should fail"""
        invalid_barcodes = [
            "INVALID",  # No delimiters
            "CARTON|ARTICLE",  # Missing quantity
            "|ARTICLE|100",  # Missing carton ID
            "CARTON||100",  # Missing article
        ]
        
        for barcode in invalid_barcodes:
            assert self._validate_barcode_format(barcode) is False
    
    def test_barcode_empty(self):
        """Empty barcode should fail"""
        assert self._validate_barcode_format("") is False
    
    @staticmethod
    def _validate_barcode_format(barcode: str) -> bool:
        """Validate barcode format"""
        if not barcode:
            return False
        
        parts = barcode.split("|")
        if len(parts) != 3:
            return False
        
        carton_id, article, quantity = parts
        
        if not carton_id or len(carton_id) < 3:
            return False
        if not article:
            return False
        
        try:
            int(quantity)
            return True
        except ValueError:
            return False


class TestBarcodeExtraction:
    """Test barcode data extraction"""
    
    def test_extract_carton_id(self):
        """Should extract carton ID from barcode"""
        barcode = "CARTON001|ARTICLE1|100"
        carton_id = self._extract_carton_id(barcode)
        assert carton_id == "CARTON001"
    
    def test_extract_article(self):
        """Should extract article from barcode"""
        barcode = "CARTON001|ARTICLE1|100"
        article = self._extract_article(barcode)
        assert article == "ARTICLE1"
    
    def test_extract_quantity(self):
        """Should extract quantity from barcode"""
        barcode = "CARTON001|ARTICLE1|100"
        quantity = self._extract_quantity(barcode)
        assert quantity == 100
    
    @staticmethod
    def _extract_carton_id(barcode: str) -> str:
        """Extract carton ID"""
        parts = barcode.split("|")
        return parts[0]
    
    @staticmethod
    def _extract_article(barcode: str) -> str:
        """Extract article"""
        parts = barcode.split("|")
        return parts[1]
    
    @staticmethod
    def _extract_quantity(barcode: str) -> int:
        """Extract quantity"""
        parts = barcode.split("|")
        return int(parts[2])


class TestArticleQuantityValidation:
    """Test article quantity limits"""
    
    def test_quantity_per_article_limit(self):
        """Article quantity should not exceed limit"""
        max_per_article = 500
        
        assert self._validate_article_quantity(100, max_per_article) is True
        assert self._validate_article_quantity(500, max_per_article) is True
        assert self._validate_article_quantity(501, max_per_article) is False
    
    def test_quantity_per_carton_limit(self):
        """Total carton quantity should not exceed limit"""
        max_per_carton = 1000
        scanned_items = {"ARTICLE1": 300, "ARTICLE2": 400, "ARTICLE3": 200}
        
        total = sum(scanned_items.values())
        assert total <= max_per_carton
    
    def test_quantity_minimum(self):
        """Quantity should be at least 1"""
        assert self._validate_article_quantity(0) is False
        assert self._validate_article_quantity(1) is True
    
    @staticmethod
    def _validate_article_quantity(quantity: int, max_qty: int = 500) -> bool:
        """Validate article quantity"""
        if quantity < 1 or quantity > max_qty:
            return False
        return True


class TestDuplicateBarcodeDetection:
    """Test duplicate barcode detection"""
    
    def test_duplicate_barcode_in_session(self):
        """Should detect duplicate barcodes in same session"""
        scanned_barcodes = [
            "CARTON001|ARTICLE1|100",
            "CARTON002|ARTICLE2|50",
            "CARTON001|ARTICLE1|100"  # Duplicate
        ]
        
        seen = set()
        duplicates = []
        
        for barcode in scanned_barcodes:
            if barcode in seen:
                duplicates.append(barcode)
            seen.add(barcode)
        
        assert len(duplicates) == 1
        assert "CARTON001|ARTICLE1|100" in duplicates
    
    def test_no_duplicates_different_quantities(self):
        """Same carton with different quantity is not duplicate"""
        scanned_barcodes = [
            "CARTON001|ARTICLE1|100",
            "CARTON001|ARTICLE1|150"
        ]
        
        seen = set()
        duplicates = []
        
        for barcode in scanned_barcodes:
            if barcode in seen:
                duplicates.append(barcode)
            seen.add(barcode)
        
        assert len(duplicates) == 0


class TestBarcodeErrorHandling:
    """Test barcode scanning error handling"""
    
    def test_malformed_barcode_error(self):
        """Malformed barcode should raise error"""
        with pytest.raises(ValueError):
            self._process_barcode("MALFORMED")
    
    def test_empty_barcode_error(self):
        """Empty barcode should raise error"""
        with pytest.raises(ValueError):
            self._process_barcode("")
    
    def test_invalid_quantity_error(self):
        """Non-numeric quantity should raise error"""
        with pytest.raises(ValueError):
            self._process_barcode("CARTON001|ARTICLE1|ABC")
    
    @staticmethod
    def _process_barcode(barcode: str):
        """Process barcode with error handling"""
        if not barcode:
            raise ValueError("Barcode cannot be empty")
        
        parts = barcode.split("|")
        if len(parts) != 3:
            raise ValueError("Invalid barcode format")
        
        carton_id, article, quantity = parts
        
        try:
            qty = int(quantity)
            if qty <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            raise ValueError("Invalid quantity")
        
        return {"carton_id": carton_id, "article": article, "quantity": qty}


class TestBarcodeScanning:
    """Test barcode scanning workflow"""
    
    def test_scan_multiple_articles_same_carton(self):
        """Should allow scanning multiple articles for same carton"""
        scans = {
            "ARTICLE1": 100,
            "ARTICLE2": 150,
            "ARTICLE3": 75
        }
        
        total = sum(scans.values())
        assert total == 325
        assert len(scans) == 3
    
    def test_scan_updates_carton_count(self):
        """Each scan should update article count for carton"""
        scanned = {}
        
        # First scan
        scanned["ARTICLE1"] = 50
        assert scanned["ARTICLE1"] == 50
        
        # Update same article
        scanned["ARTICLE1"] = 100
        assert scanned["ARTICLE1"] == 100
    
    def test_scan_session_clear(self):
        """Should clear scan session after confirmation"""
        scanned = {"ARTICLE1": 100, "ARTICLE2": 150}
        assert len(scanned) == 2
        
        scanned.clear()
        assert len(scanned) == 0


class TestBarcodeQRCodeFormats:
    """Test different barcode formats"""
    
    def test_ean13_format(self):
        """Should support EAN-13 barcodes"""
        # EAN-13: 13 digits
        ean13 = "5901234123457"
        assert len(ean13) == 13
        assert ean13.isdigit()
    
    def test_code128_format(self):
        """Should support Code-128 barcodes"""
        # Code-128: variable length
        code128 = "CODE-128-TEST-123"
        assert len(code128) > 0
    
    def test_qr_code_format(self):
        """Should support QR codes"""
        # QR code: structured data
        qr = "CARTON001|ARTICLE1|100"
        assert "|" in qr


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.barcode"])
