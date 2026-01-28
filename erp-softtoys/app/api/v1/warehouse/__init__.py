"""Warehouse API Module - Submodules
This folder contains warehouse-related submodules.
Main warehouse endpoints are in warehouse_endpoints.py.
"""
from app.api.v1.warehouse.material_debt import router as material_debt_router

__all__ = ["material_debt_router"]
