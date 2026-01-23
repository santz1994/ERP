"""
Pytest configuration and shared fixtures
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.models.users import User, UserRole
from app.core.security import PasswordUtils, TokenUtils
from app.main import app

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
test_client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create tables for testing"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Database session fixture"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Test client fixture"""
    return test_client


@pytest.fixture
def admin_user(db):
    """Create admin user for testing"""
    admin = User(
        username="admin",
        email="admin@test.com",
        hashed_password=PasswordUtils.hash_password("Admin@123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def admin_token(admin_user):
    """Generate admin JWT token"""
    return TokenUtils.create_access_token(
        user_id=admin_user.id,
        username=admin_user.username,
        email=admin_user.email,
        roles=["Admin"]
    )


@pytest.fixture
def admin_headers(admin_token):
    """Admin authorization headers"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test@123",
        "full_name": "Test User",
        "roles": ["operator_cutting"]
    }


# ===== ROLE-BASED USERS & TOKENS =====

@pytest.fixture
def operator_user(db):
    """Create operator user"""
    operator = User(
        username="operator_cutting",
        email="operator@test.com",
        hashed_password=PasswordUtils.hash_password("Op@123"),
        full_name="Operator User",
        role=UserRole.OPERATOR_CUTTING,
        is_active=True,
        is_verified=True
    )
    db.add(operator)
    db.commit()
    db.refresh(operator)
    return operator


@pytest.fixture
def operator_token(operator_user):
    """Generate operator JWT token"""
    return TokenUtils.create_access_token(
        user_id=operator_user.id,
        username=operator_user.username,
        email=operator_user.email,
        roles=["Operator_Cutting"]
    )


@pytest.fixture
def supervisor_user(db):
    """Create supervisor user"""
    supervisor = User(
        username="spv_cutting",
        email="supervisor@test.com",
        hashed_password=PasswordUtils.hash_password("Spv@123"),
        full_name="Supervisor User",
        role=UserRole.SPV_CUTTING,
        is_active=True,
        is_verified=True
    )
    db.add(supervisor)
    db.commit()
    db.refresh(supervisor)
    return supervisor


@pytest.fixture
def supervisor_token(supervisor_user):
    """Generate supervisor JWT token"""
    return TokenUtils.create_access_token(
        user_id=supervisor_user.id,
        username=supervisor_user.username,
        email=supervisor_user.email,
        roles=["SPV_Cutting"]
    )


@pytest.fixture
def qc_user(db):
    """Create QC inspector user"""
    qc = User(
        username="qc_inspector",
        email="qc@test.com",
        hashed_password=PasswordUtils.hash_password("QC@123"),
        full_name="QC Inspector",
        role=UserRole.QC_INSPECTOR,
        is_active=True,
        is_verified=True
    )
    db.add(qc)
    db.commit()
    db.refresh(qc)
    return qc


@pytest.fixture
def qc_token(qc_user):
    """Generate QC JWT token"""
    return TokenUtils.create_access_token(
        user_id=qc_user.id,
        username=qc_user.username,
        email=qc_user.email,
        roles=["QC_Inspector"]
    )


@pytest.fixture
def warehouse_user(db):
    """Create warehouse admin user"""
    warehouse = User(
        username="warehouse_admin",
        email="warehouse@test.com",
        hashed_password=PasswordUtils.hash_password("WH@123"),
        full_name="Warehouse Admin",
        role=UserRole.WAREHOUSE_ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@pytest.fixture
def warehouse_token(warehouse_user):
    """Generate warehouse JWT token"""
    return TokenUtils.create_access_token(
        user_id=warehouse_user.id,
        username=warehouse_user.username,
        email=warehouse_user.email,
        roles=["Warehouse_Admin"]
    )


# ===== SAMPLE PRODUCTS & DATA =====

@pytest.fixture
def sample_product(db):
    """Create sample product for testing"""
    from app.core.models.products import Category, Product, ProductType

    # Create category if needed
    category = Category(name="Soft Toys", description="Stuffed animals")
    db.add(category)
    db.commit()

    # Create product
    product = Product(
        code="BLAHAJ-BLUE",
        name="Blahaj Shark",
        type=ProductType.RAW_MATERIAL,
        uom="Pcs",
        category_id=category.id,
        min_stock=100
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def sample_manufacturing_order(db, sample_product):
    """Create sample manufacturing order"""
    from app.core.models.manufacturing import ManufacturingOrder, RoutingType

    mo = ManufacturingOrder(
        so_line_id=1,
        product_id=sample_product.id,
        qty_planned=100,
        routing_type=RoutingType.ROUTE1,
        batch_number="BATCH-001",
        state="Draft"
    )
    db.add(mo)
    db.commit()
    db.refresh(mo)
    return mo


@pytest.fixture
def sample_work_order(db, sample_manufacturing_order):
    """Create sample work order"""
    from app.core.models.manufacturing import Department, WorkOrder, WorkOrderStatus

    wo = WorkOrder(
        mo_id=sample_manufacturing_order.id,
        department=Department.CUTTING,
        status=WorkOrderStatus.PENDING,
        input_qty=100,
        output_qty=0
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo


@pytest.fixture
def sample_transfer_log(db, sample_work_order):
    """Create sample transfer log"""
    from app.core.models.transfer import Department, TransferLog

    transfer = TransferLog(
        work_order_id=sample_work_order.id,
        from_dept=Department.CUTTING,
        to_dept=Department.SEWING,
        article_code="WIP-CUT-001",
        qty_sent=100,
        qty_received=0,
        is_line_clear=True,
        timestamp_start=datetime.utcnow()
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


# ===== UTILITIES =====

@pytest.fixture
def clear_db(db):
    """Clear database before each test"""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()


@pytest.fixture(autouse=True)
def reset_db_per_test(db):
    """Auto-reset database per test"""
    yield
    db.rollback()
