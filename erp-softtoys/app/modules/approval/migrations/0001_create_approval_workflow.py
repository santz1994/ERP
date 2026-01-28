"""
Database Migration: Add Approval Workflow Tables
Date: 28 Januari 2026
Feature: #2 - Approval Workflow Multi-Level

Tables Created:
1. approval_requests - Main approval request table
2. approval_steps - Individual approval steps
3. approval_history - Audit trail for approval actions
"""

# Migration ID: 2026_01_28_001_approval_workflow

def upgrade():
    """Create approval workflow tables"""
    
    # Create approval_requests table
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('entity_type', sa.String(50), nullable=False),  # SPK_CREATE, SPK_EDIT_QUANTITY, etc
        sa.Column('entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('submitted_by', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('changes', sa.JSON, nullable=False),  # JSON of changes
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), nullable=False),  # PENDING, APPROVED, REJECTED, etc
        sa.Column('current_step', sa.Integer, default=0),  # Which step in approval chain (0=SPV, 1=Manager)
        sa.Column('approval_chain', sa.JSON, nullable=False),  # [SPV, MANAGER, DIRECTOR]
        sa.Column('approvals', sa.JSON),  # Array of approval steps with timestamps
        sa.Column('rejection_reason', sa.Text),
        sa.Column('rejected_by', sa.UUID(as_uuid=True)),
        sa.Column('rejected_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.now),
        sa.Column('updated_at', sa.DateTime, default=datetime.now, onupdate=datetime.now),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id']),
        sa.Index('idx_approval_requests_entity', 'entity_type', 'entity_id'),
        sa.Index('idx_approval_requests_status', 'status'),
        sa.Index('idx_approval_requests_created', 'created_at'),
    )
    
    # Create approval_steps table (detailed step tracking)
    op.create_table(
        'approval_steps',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('approval_request_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('step_number', sa.Integer, nullable=False),  # 1=SPV, 2=Manager, 3=Director
        sa.Column('approver_role', sa.String(50), nullable=False),  # SPV, MANAGER, DIRECTOR
        sa.Column('status', sa.String(20), nullable=False),  # PENDING, APPROVED, REJECTED
        sa.Column('approved_by', sa.UUID(as_uuid=True)),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('notes', sa.Text),  # Approver notes
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.now),
        sa.ForeignKeyConstraint(['approval_request_id'], ['approval_requests.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.Index('idx_approval_steps_request', 'approval_request_id'),
        sa.Index('idx_approval_steps_status', 'status'),
    )


def downgrade():
    """Rollback approval workflow tables"""
    op.drop_table('approval_steps')
    op.drop_table('approval_requests')
