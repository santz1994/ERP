"""
Internationalization (i18n) Module - Multi-language support
Supports: Indonesia (id) and English (en)
"""
from typing import Dict

# Language translations
TRANSLATIONS = {
    "en": {
        # Authentication & Authorization
        "auth.login.success": "Login successful",
        "auth.login.failed": "Invalid username or password",
        "auth.logout.success": "Logout successful",
        "auth.token.expired": "Token has expired",
        "auth.token.invalid": "Invalid token",
        "auth.permission.denied": "Permission denied",
        "auth.account.locked": "Account locked due to too many failed attempts",
        
        # Products & Inventory
        "product.not_found": "Product not found",
        "product.created": "Product created successfully",
        "product.updated": "Product updated successfully",
        "product.deleted": "Product deleted successfully",
        "product.code_exists": "Product code already exists",
        "inventory.low_stock": "Low stock alert for {product_name}",
        "inventory.out_of_stock": "Out of stock: {product_name}",
        
        # Manufacturing
        "mo.created": "Manufacturing Order created",
        "mo.approved": "Manufacturing Order approved",
        "mo.completed": "Manufacturing Order completed",
        "mo.cancelled": "Manufacturing Order cancelled",
        "wo.started": "Work Order started",
        "wo.finished": "Work Order finished",
        "wo.shortage": "Shortage detected: {qty} units short",
        "wo.surplus": "Surplus detected: {qty} units extra",
        
        # Transfer & Line Clearance
        "transfer.initiated": "Transfer initiated",
        "transfer.received": "Transfer received",
        "transfer.line_clearance_required": "Line clearance required before transfer",
        "transfer.line_occupied": "Line still occupied with {article}",
        "transfer.segregation_alert": "Segregation alert: Different destination detected",
        
        # Quality Control
        "qc.test.pass": "QC Test passed",
        "qc.test.fail": "QC Test failed",
        "qc.inspection.required": "Inspection required",
        "qc.defect.detected": "Defect detected: {reason}",
        "qc.metal_detector.pass": "Metal detector check passed",
        "qc.metal_detector.fail": "Metal detector check failed - Contamination detected",
        
        # Warehouse
        "warehouse.material_issued": "Material issued",
        "warehouse.stock_adjusted": "Stock adjusted",
        "warehouse.location_not_found": "Location not found",
        
        # Common
        "success": "Success",
        "error": "Error",
        "validation_error": "Validation error",
        "not_found": "Not found",
        "created": "Created successfully",
        "updated": "Updated successfully",
        "deleted": "Deleted successfully",
        "cancelled": "Cancelled",
        "approved": "Approved",
        "rejected": "Rejected",
        "pending": "Pending",
        "in_progress": "In Progress",
        "completed": "Completed",
    },
    "id": {
        # Authentication & Authorization
        "auth.login.success": "Login berhasil",
        "auth.login.failed": "Username atau password salah",
        "auth.logout.success": "Logout berhasil",
        "auth.token.expired": "Token sudah kadaluarsa",
        "auth.token.invalid": "Token tidak valid",
        "auth.permission.denied": "Akses ditolak",
        "auth.account.locked": "Akun terkunci karena terlalu banyak percobaan gagal",
        
        # Products & Inventory
        "product.not_found": "Produk tidak ditemukan",
        "product.created": "Produk berhasil dibuat",
        "product.updated": "Produk berhasil diupdate",
        "product.deleted": "Produk berhasil dihapus",
        "product.code_exists": "Kode produk sudah ada",
        "inventory.low_stock": "Peringatan stok rendah untuk {product_name}",
        "inventory.out_of_stock": "Stok habis: {product_name}",
        
        # Manufacturing
        "mo.created": "Manufacturing Order dibuat",
        "mo.approved": "Manufacturing Order disetujui",
        "mo.completed": "Manufacturing Order selesai",
        "mo.cancelled": "Manufacturing Order dibatalkan",
        "wo.started": "Work Order dimulai",
        "wo.finished": "Work Order selesai",
        "wo.shortage": "Kekurangan terdeteksi: kurang {qty} unit",
        "wo.surplus": "Kelebihan terdeteksi: lebih {qty} unit",
        
        # Transfer & Line Clearance
        "transfer.initiated": "Transfer dimulai",
        "transfer.received": "Transfer diterima",
        "transfer.line_clearance_required": "Line clearance diperlukan sebelum transfer",
        "transfer.line_occupied": "Line masih terisi dengan {article}",
        "transfer.segregation_alert": "Peringatan segregasi: Destinasi berbeda terdeteksi",
        
        # Quality Control
        "qc.test.pass": "Tes QC lulus",
        "qc.test.fail": "Tes QC gagal",
        "qc.inspection.required": "Inspeksi diperlukan",
        "qc.defect.detected": "Cacat terdeteksi: {reason}",
        "qc.metal_detector.pass": "Pemeriksaan metal detector lulus",
        "qc.metal_detector.fail": "Pemeriksaan metal detector gagal - Kontaminasi terdeteksi",
        
        # Warehouse
        "warehouse.material_issued": "Material dikeluarkan",
        "warehouse.stock_adjusted": "Stok disesuaikan",
        "warehouse.location_not_found": "Lokasi tidak ditemukan",
        
        # Common
        "success": "Berhasil",
        "error": "Error",
        "validation_error": "Error validasi",
        "not_found": "Tidak ditemukan",
        "created": "Berhasil dibuat",
        "updated": "Berhasil diupdate",
        "deleted": "Berhasil dihapus",
        "cancelled": "Dibatalkan",
        "approved": "Disetujui",
        "rejected": "Ditolak",
        "pending": "Menunggu",
        "in_progress": "Sedang Proses",
        "completed": "Selesai",
    }
}


class I18n:
    """Internationalization handler"""
    
    def __init__(self, lang: str = "id"):
        """
        Initialize i18n with language
        
        Args:
            lang: Language code ('en' or 'id')
        """
        self.lang = lang if lang in TRANSLATIONS else "id"
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate key to current language
        
        Args:
            key: Translation key (e.g., 'auth.login.success')
            **kwargs: Format parameters
        
        Returns:
            Translated string
        
        Example:
            i18n = I18n('id')
            i18n.t('inventory.low_stock', product_name='Blue Shark')
            # Output: 'Peringatan stok rendah untuk Blue Shark'
        """
        translation = TRANSLATIONS[self.lang].get(key, key)
        if kwargs:
            return translation.format(**kwargs)
        return translation
    
    def set_language(self, lang: str):
        """Change language"""
        if lang in TRANSLATIONS:
            self.lang = lang
    
    def get_language(self) -> str:
        """Get current language"""
        return self.lang
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(TRANSLATIONS.keys())


def get_i18n(lang: str = "id") -> I18n:
    """
    Get i18n instance
    
    Args:
        lang: Language code from request header (Accept-Language)
    
    Returns:
        I18n instance
    """
    return I18n(lang)


# FastAPI dependency
from fastapi import Header

async def get_translation(accept_language: str = Header("id")) -> I18n:
    """
    FastAPI dependency for i18n
    
    Usage in route:
        @router.get("/example")
        async def example(i18n: I18n = Depends(get_translation)):
            return {"message": i18n.t("success")}
    
    Client can set language via header:
        curl -H "Accept-Language: en" http://localhost:8000/api/example
    """
    # Extract primary language from header (e.g., "en-US" -> "en", "id-ID" -> "id")
    lang = accept_language.split("-")[0].lower() if accept_language else "id"
    return get_i18n(lang)
