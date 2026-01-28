# 🚀 APPROVAL WORKFLOW - QUICK START GUIDE

**For**: Developers, DevOps, QA Team  
**Purpose**: Understand and use Feature #2 - Approval Workflow Multi-Level

---

## 📋 QUICK REFERENCE

### What is Feature #2?

Multi-level approval system where certain changes require approval from supervisors and managers before being executed.

**Example**: Creating a new SPK requires approval from:
1. SPV (Supervisor) - First approver
2. MANAGER - Second approver
3. DIRECTOR - Notified (read-only, no action)

### What Gets Approved?

| Entity | Approvers | Use Case |
|--------|-----------|----------|
| **SPK_CREATE** | SPV → MANAGER | Creating new production order |
| **SPK_EDIT_QUANTITY** | SPV → MANAGER | Changing production quantity |
| **SPK_EDIT_DEADLINE** | SPV → MANAGER | Changing deadline |
| **MO_EDIT** | MANAGER only | Modifying manufacturing order |
| **MATERIAL_DEBT** | SPV → MANAGER | Handling material shortage |
| **STOCK_ADJUSTMENT** | SPV → MANAGER | Stock count corrections |

---

## 🔧 FOR DEVELOPERS

### 1. Use the Approval Service

```python
from app.services.approval_service import ApprovalWorkflowEngine, ApprovalEntityType
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize engine
approval_engine = ApprovalWorkflowEngine()

# Submit for approval
result = await approval_engine.submit_for_approval(
    entity_type=ApprovalEntityType.SPK_CREATE,
    entity_id=spk_id,  # UUID of the SPK
    changes={
        "title": "New Production Order",
        "deadline": "2026-02-15",
        "quantity": 500
    },
    reason="Customer urgent order",
    submitted_by=user_id,  # UUID of current user
    session=session,  # AsyncSession
)

# Returns:
# {
#   "approval_request_id": "uuid",
#   "status": "PENDING",
#   "approval_chain": ["SPV", "MANAGER"],
#   "current_step": 0,
#   "next_approver": "SPV"
# }
```

### 2. Call Approval Endpoints

```python
# Submit for approval
POST /api/v1/approvals/submit
{
    "entity_type": "SPK_CREATE",
    "entity_id": "123e4567-e89b-12d3-a456-426614174000",
    "changes": {"quantity": 500},
    "reason": "Customer request"
}

# Approve
PUT /api/v1/approvals/{approval_id}/approve
{
    "notes": "Looks good, approved"
}

# Reject
PUT /api/v1/approvals/{approval_id}/reject
{
    "reason": "Does not meet standards"
}

# Get pending approvals for user
GET /api/v1/approvals/my-pending?entity_type=SPK_CREATE&limit=50

# Get approval history
GET /api/v1/approvals/{approval_id}/history
```

### 3. Handle Approval in Your Feature

```python
# When creating a new SPK with approval:

async def create_spk_with_approval(
    title: str,
    deadline: date,
    quantity: int,
    current_user: User,
    session: AsyncSession,
):
    # Step 1: Submit for approval
    approval = await approval_engine.submit_for_approval(
        entity_type=ApprovalEntityType.SPK_CREATE,
        entity_id=spk_id,  # Temporary ID or generate new
        changes={
            "title": title,
            "deadline": deadline.isoformat(),
            "quantity": quantity
        },
        reason="User initiated SPK creation",
        submitted_by=current_user.id,
        session=session,
    )
    
    # Step 2: Return approval status to frontend
    return {
        "status": "PENDING_APPROVAL",
        "approval_request_id": approval["approval_request_id"],
        "message": f"Waiting approval from {approval['next_approver']}"
    }

# When approval is completed by the backend/service:

async def on_spk_approval_complete(approval_id: UUID, session: AsyncSession):
    approval = await approval_engine._get_approval_request(approval_id, session)
    
    if approval.status == ApprovalStatus.APPROVED:
        # Create actual SPK now
        spk = SPK(
            title=approval.changes["title"],
            deadline=approval.changes["deadline"],
            quantity=approval.changes["quantity"],
            status="PENDING_PRODUCTION"
        )
        session.add(spk)
        await session.commit()
        
        # Notify user
        await send_notification(
            user_id=approval.submitted_by,
            message="Your SPK has been approved and is ready for production"
        )
```

---

## 🎨 FOR FRONTEND DEVELOPERS

### Using Approval Components

```tsx
import ApprovalFlow from '@/components/ApprovalFlow';
import MyApprovalsPage from '@/pages/MyApprovalsPage';
import ApprovalModal from '@/components/ApprovalModal';

// 1. Show approval timeline
<ApprovalFlow
  steps={approval.approval_steps}
  current_step={approval.current_step}
  approval_chain={approval.approval_chain}
  status={approval.status}
/>

// 2. Show all pending approvals for user
<MyApprovalsPage />

// 3. Approve/Reject dialog
<ApprovalModal
  approval={selectedApproval}
  actionType="approve"  // or "reject"
  onClose={() => setShowModal(false)}
  onSuccess={() => refreshApprovals()}
/>
```

### Example Page Integration

```tsx
import { useEffect, useState } from 'react';
import MyApprovalsPage from '@/pages/MyApprovalsPage';
import ApprovalFlow from '@/components/ApprovalFlow';

export default function Dashboard() {
  const [pending, setPending] = useState(0);

  useEffect(() => {
    // Fetch count of pending approvals
    fetch('/api/v1/approvals/my-pending')
      .then(r => r.json())
      .then(data => setPending(data.length));
  }, []);

  return (
    <div className="dashboard">
      {/* Show notification badge */}
      <div className="notification-badge">
        {pending > 0 && <span className="badge-red">{pending}</span>}
      </div>

      {/* Route to approval page when user clicks */}
      <Route path="/approvals" element={<MyApprovalsPage />} />
    </div>
  );
}
```

### Styling Reference

```tsx
// Status colors used in components:
const statusColors = {
  PENDING: 'bg-yellow-100 text-yellow-800',      // Yellow - waiting
  SPV_APPROVED: 'bg-blue-100 text-blue-800',     // Blue - SPV done
  MANAGER_APPROVED: 'bg-purple-100 text-purple-800', // Purple - Manager done
  APPROVED: 'bg-green-100 text-green-800',       // Green - fully approved
  REJECTED: 'bg-red-100 text-red-800',           // Red - rejected
};

// Entity type colors:
const entityColors = {
  SPK_CREATE: 'bg-blue-100 text-blue-800',
  SPK_EDIT_QUANTITY: 'bg-purple-100 text-purple-800',
  MO_EDIT: 'bg-green-100 text-green-800',
  MATERIAL_DEBT: 'bg-red-100 text-red-800',
};
```

---

## 📧 FOR DEVOPS / EMAIL SETUP

### Configure Email Service

In `.env` file:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=erp@qutykarunia.co.id
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=erp@qutykarunia.co.id
SMTP_FROM_NAME=ERP Quty Karunia
SMTP_USE_TLS=true
```

### Initialize Email Service

In `main.py`:
```python
from app.services.approval_email_service import init_approval_email_service

@app.on_event("startup")
async def startup():
    # Initialize approval email service
    smtp_config = {
        'smtp_host': settings.SMTP_HOST,
        'smtp_port': settings.SMTP_PORT,
        'smtp_user': settings.SMTP_USER,
        'smtp_password': settings.SMTP_PASSWORD,
        'from_email': settings.SMTP_FROM_EMAIL,
        'from_name': settings.SMTP_FROM_NAME,
        'smtp_use_tls': settings.SMTP_USE_TLS,
    }
    init_approval_email_service(smtp_config)
```

### Email Template Customization

Edit `/app/templates/emails/ppic_approval_request.html`:
- Change colors (brand colors in CSS)
- Modify company name/info in footer
- Update button URLs
- Customize email copy

---

## 🧪 FOR QA TESTING

### Test Scenarios

**Scenario 1: Complete SPK Approval Flow**
1. User submits SPK_CREATE via API
2. SPV receives email → Opens dashboard
3. SPV approves → Check status changes to SPV_APPROVED
4. Manager receives email → Opens dashboard
5. Manager approves → Check status changes to APPROVED
6. Verify: Director gets notified (read-only)

**Scenario 2: Rejection Flow**
1. User submits SPK_CREATE
2. SPV approves
3. Manager rejects with reason "Quantity too high"
4. Verify: Status = REJECTED
5. Verify: Submitter gets notification with reason

**Scenario 3: Component Display**
1. Navigate to /approvals
2. Verify: ApprovalFlow timeline shows all steps
3. Verify: Current step is highlighted with animation
4. Verify: Colors match: green (done), yellow (current), gray (waiting)

**Scenario 4: Email Notifications**
1. Submit approval → Check email received within 5 seconds
2. Verify: Email contains: entity type, changes, approver action links
3. Verify: Click approval link → Opens dashboard with item selected

### Test Data Queries

```sql
-- View all pending approvals
SELECT * FROM approval_requests 
WHERE status = 'PENDING' 
ORDER BY created_at DESC;

-- View approval history for specific entity
SELECT * FROM approval_requests 
WHERE entity_type = 'SPK_CREATE' 
AND entity_id = '...' 
ORDER BY created_at DESC;

-- Count approvals by step
SELECT current_step, COUNT(*) 
FROM approval_requests 
WHERE status = 'PENDING' 
GROUP BY current_step;

-- View approval steps detail
SELECT ar.entity_type, ar.current_step, ast.* 
FROM approval_requests ar 
JOIN approval_steps ast ON ar.id = ast.approval_request_id 
WHERE ar.id = '...' 
ORDER BY ast.step_number;
```

---

## 🔍 TROUBLESHOOTING

### Email Not Sending?
1. Check `.env` SMTP settings
2. Verify email service initialized in app startup
3. Check logs: `grep -i "email\|smtp" /var/log/app.log`
4. Test manually: `python -m app.services.approval_email_service --test`

### Approval Not Appearing?
1. Check user has correct role in `user_roles` table
2. Verify approval_request in database:
   ```sql
   SELECT * FROM approval_requests WHERE approval_request_id = '...';
   ```
3. Check `current_step` matches user's approver role

### Frontend Component Not Loading?
1. Check network tab in browser DevTools
2. Verify API endpoint returns data
3. Check console for JavaScript errors
4. Verify: `date-fns`, `lucide-react` packages installed

### Performance Issues?
1. Add index on `approval_requests(status, current_step)`
2. Cache pending approvals count in Redis
3. Paginate approval list (default limit=50)

---

## 📚 RELATED FILES

**Backend**:
- `/app/services/approval_service.py` - Core logic
- `/app/services/approval_email_service.py` - Email notifications
- `/app/api/approvals.py` - API endpoints
- `/app/modules/approval/migrations/0001_create_approval_workflow.py` - DB schema

**Frontend**:
- `/src/components/ApprovalFlow.tsx` - Timeline component
- `/src/pages/MyApprovalsPage.tsx` - Approval dashboard
- `/src/components/ApprovalModal.tsx` - Action dialog

**Tests**:
- `/tests/test_approval_workflow.py` - Unit tests

**Documentation**:
- `/docs/Project.md` - Feature specifications
- `/docs/IMPLEMENTATION_CHECKLIST_12_FEATURES.md` - Implementation progress

---

## 🚀 QUICK COMMANDS

```bash
# Run tests
pytest tests/test_approval_workflow.py -v

# Run specific test
pytest tests/test_approval_workflow.py::TestApprovalWorkflowEngine::test_submit_for_approval_spk_create -v

# Check email service
python -c "from app.services.approval_email_service import ApprovalEmailService; print('✅ Service OK')"

# View pending approvals
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/approvals/my-pending?limit=10

# Test approval endpoint
curl -X POST http://localhost:8000/api/v1/approvals/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "entity_type": "SPK_CREATE",
    "entity_id": "123e4567-e89b-12d3-a456-426614174000",
    "changes": {"quantity": 500},
    "reason": "Test submission"
  }'
```

---

## 📞 SUPPORT

- **Questions**: Check `/docs/SESSION_35_FEATURE2_IMPLEMENTATION_SUMMARY.md`
- **Issues**: Create issue with tag `feature/approval-workflow`
- **Email**: erp-support@qutykarunia.co.id

---

**Version**: 1.0  
**Last Updated**: 28 January 2026  
**Status**: ✅ Production Ready
