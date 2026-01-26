# 🔬 PHASE 3 DEEP TESTING ANALYSIS & RECOMMENDATIONS

**Date**: January 26, 2026 - Deep Analysis Session  
**Analysis Scope**: Full Phase 3 code review + testing strategy + staging + CI/CD + monitoring  
**Objective**: Identify issues, provide recommendations, design production infrastructure  

---

## 📊 DEEP TESTING ANALYSIS

### PART 1: KOTLIN ANDROID APP - CODE REVIEW

#### **1.1 LoginScreen.kt & LoginViewModel.kt Analysis**

**Potential Issues Found:**

```kotlin
// ISSUE 1: Password validation too lenient
fun login(username: String, password: String, rememberMe: Boolean) {
    // Problem: Min 6 chars only, no special character requirement
    if (password.length < 6) {
        setError("Password minimal 6 karakter")
        return
    }
    // Solution: Add complexity requirement
}

// ISSUE 2: 2FA PIN bypass risk
fun confirmPin(pin: String) {
    // Problem: No rate limiting on PIN attempts
    // User dapat brute force 6-digit PIN (10^6 = 1 juta kombinasi)
    if (pin.length != 6 || !pin.all { it.isDigit() }) {
        setError("PIN harus 6 digit")
        return
    }
    // Solution: Add attempt counter + lockout
}

// ISSUE 3: Token refresh timing
// Problem: Token refresh hanya saat doWork(), not proactive
// Solution: Refresh 5 min sebelum expiry, not saat terakhir detik
```

**Recommendations:**

✅ **Password Requirements** (Priority: HIGH)
```kotlin
// Add complexity check:
- Minimum 8 characters (not 6)
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character

Implementation:
fun isPasswordStrong(password: String): Boolean {
    return password.length >= 8 &&
           password.any { it.isUpperCase() } &&
           password.any { it.isDigit() } &&
           password.any { it in "!@#$%^&*()" }
}
```

✅ **2FA PIN Brute Force Protection** (Priority: HIGH)
```kotlin
// Add rate limiting:
data class PinAttempt(
    val userId: String,
    val attempts: Int = 0,
    val lastAttemptTime: LocalDateTime,
    val isLocked: Boolean = false,
    val lockUntil: LocalDateTime? = null
)

// Rules:
- Max 3 attempts per minute
- Lock for 15 minutes after 3 failures
- Log all failed attempts
- Alert after 5 minutes of continuous failures
```

✅ **Proactive Token Refresh** (Priority: HIGH)
```kotlin
// In TokenRefreshWorker:
fun refresh() {
    val currentTime = System.currentTimeMillis()
    val expiryTime = getTokenExpiry() // dari SharedPreferences
    val timeUntilExpiry = expiryTime - currentTime
    
    // Refresh jika kurang dari 5 menit
    if (timeUntilExpiry < 5 * 60 * 1000) {
        callRefreshEndpoint()
    }
}
```

---

#### **1.2 DailyProductionInputScreen.kt & ViewModel Analysis**

**Potential Issues Found:**

```kotlin
// ISSUE 1: No input validation on daily quantity
fun setDailyInput(date: LocalDate, quantity: Int) {
    // Problem: Quantity bisa negative, bisa exceed target drastis
    dailyInputs[date] = quantity  // Langsung assign tanpa check
    
    // Solution: Add min/max validation
}

// ISSUE 2: Cumulative calculation error
fun calculateCumulative(): Int {
    // Problem: Tidak handle duplicate entries atau overwrites
    // Bisa double-count jika user edit same day twice
    return dailyInputs.values.sum()
}

// ISSUE 3: UI not responsive to rapid clicks
// User dapat click "Save" multiple times
// Bisa kirim duplicate requests ke backend
```

**Recommendations:**

✅ **Input Validation** (Priority: HIGH)
```kotlin
fun setDailyInput(date: LocalDate, quantity: Int): Result<Unit> {
    return when {
        quantity < 0 -> {
            Result.failure(Exception("Quantity tidak boleh negative"))
        }
        quantity > targetQty * 2 -> {
            Result.failure(Exception("Quantity terlalu tinggi (maks: ${targetQty * 2})"))
        }
        date > LocalDate.now() -> {
            Result.failure(Exception("Tidak boleh input tanggal masa depan"))
        }
        else -> {
            dailyInputs[date] = quantity
            Result.success(Unit)
        }
    }
}
```

✅ **Prevent Duplicate Requests** (Priority: MEDIUM)
```kotlin
// Add debouncing untuk save button
fun saveProgress() {
    if (isSaving) return  // Skip jika sedang save
    
    isSaving = true
    viewModelScope.launch {
        try {
            api.recordDailyInput(...)
            showSuccess()
        } finally {
            isSaving = false
        }
    }
}
```

✅ **Cumulative Calculation Safety** (Priority: MEDIUM)
```kotlin
// Add transaction-like logic:
fun calculateCumulativeWithAudit(): Pair<Int, List<DailyEntry>> {
    val entries = dailyInputs.entries
        .sortedBy { it.key }
        .map { DailyEntry(date = it.key, qty = it.value) }
    
    val total = entries.sumOf { it.qty }
    
    // Validate consistency
    require(total <= targetQty * 2, { "Cumulative exceeds reasonable limit" })
    
    return Pair(total, entries)
}
```

---

#### **1.3 FinishGoodBarcodeScreen.kt & ViewModel Analysis**

**Potential Issues Found:**

```kotlin
// ISSUE 1: Barcode parsing vulnerable to malformed input
fun extractCartonId(barcodeData: String): String {
    // Problem: No validation, could crash on invalid format
    return barcodeData.split("|")[0]  // IndexOutOfBounds risk
}

// ISSUE 2: Article counting no upper limit
fun incrementCount(articleId: String) {
    // Problem: Can count infinite items, no max per carton
    val current = scannedItems[articleId] ?: 0
    scannedItems[articleId] = current + 1  // No limit check
}

// ISSUE 3: Offline queue not clearing properly
// Sync items bisa stuck di queue forever jika network persis down
```

**Recommendations:**

✅ **Barcode Parsing Robustness** (Priority: HIGH)
```kotlin
fun extractCartonId(barcodeData: String): Result<String> {
    return try {
        val parts = barcodeData.split("|")
        when {
            parts.isEmpty() -> Result.failure(Exception("Invalid barcode format"))
            parts[0].isEmpty() -> Result.failure(Exception("Carton ID empty"))
            parts[0].length < 3 -> Result.failure(Exception("Carton ID too short"))
            else -> Result.success(parts[0])
        }
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

✅ **Article Quantity Limits** (Priority: HIGH)
```kotlin
data class ArticleLimit(
    val articleId: String,
    val maxPerCarton: Int = 500,  // Reasonable max
    val maxPerArticle: Int = 200   // Sanity check
)

fun incrementCount(articleId: String, limits: ArticleLimit): Result<Unit> {
    val current = scannedItems[articleId] ?: 0
    val total = scannedItems.values.sum()
    
    return when {
        current >= limits.maxPerArticle -> {
            Result.failure(Exception("Article max reached: ${limits.maxPerArticle}"))
        }
        total >= limits.maxPerCarton -> {
            Result.failure(Exception("Carton capacity exceeded"))
        }
        else -> {
            scannedItems[articleId] = current + 1
            Result.success(Unit)
        }
    }
}
```

✅ **Sync Queue Cleanup** (Priority: MEDIUM)
```kotlin
// Di SyncWorker:
fun doWork(): Result {
    // Add timeout: jika item stuck > 24 jam, mark as failed
    val stuckItems = repository.getPendingSyncItems()
        .filter { it.createdAt.plusHours(24) < LocalDateTime.now() }
    
    stuckItems.forEach { item ->
        repository.markAsFailed(item.id, "Sync timeout after 24h")
        alertManager.notify(
            "Sync item ${item.id} failed after 24 hours, manual review needed"
        )
    }
    
    return Result.retry()
}
```

---

#### **1.4 Database & Repository Analysis**

**Potential Issues Found:**

```kotlin
// ISSUE 1: No transaction management
// Jika sync halfway, data bisa inconsistent
override suspend fun syncPendingInputs(): Result<Int> {
    val items = dao.getPendingSyncItems()
    
    // Problem: Tidak atomic, error tengah jalan bisa corrupt data
    items.forEach { item ->
        api.send(item)
        dao.markAsSynced(item.id)
    }
    
    return Result.success(items.size)
}

// ISSUE 2: No foreign key constraints
// Bisa orphaned records jika parent deleted
// No cascade delete settings

// ISSUE 3: Room version mismatch handling
// Jika upgrade database schema, no migration path
```

**Recommendations:**

✅ **Transaction Management** (Priority: HIGH)
```kotlin
override suspend fun syncPendingInputs(): Result<Int> {
    return try {
        var successCount = 0
        database.withTransaction {
            val items = dao.getPendingSyncItems()
            
            for (item in items) {
                try {
                    val response = api.send(item)
                    if (response.isSuccessful) {
                        dao.markAsSynced(item.id)
                        successCount++
                    } else {
                        throw HttpException("API rejected: ${response.code}")
                    }
                } catch (e: Exception) {
                    // Transaction rollback occurs automatically
                    throw e
                }
            }
        }
        Result.success(successCount)
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

✅ **Foreign Key Constraints** (Priority: HIGH)
```kotlin
@Entity(
    tableName = "daily_production_input",
    foreignKeys = [
        ForeignKey(
            entity = SPK::class,
            parentColumns = ["id"],
            childColumns = ["spk_id"],
            onDelete = ForeignKey.CASCADE  // Cascade delete
        )
    ]
)
data class DailyProductionInput(
    @PrimaryKey val id: String,
    @ColumnInfo val spk_id: Int,
    // ... other fields
)
```

✅ **Database Migration Strategy** (Priority: HIGH)
```kotlin
@Database(
    entities = [
        OfflineSyncEntity::class,
        DailyProductionCacheEntity::class,
        FinishGoodCacheEntity::class,
        UserSessionEntity::class
    ],
    version = 2,  // Incremented from 1
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    companion object {
        private val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                // Add new column with default value
                database.execSQL(
                    "ALTER TABLE daily_production_input ADD COLUMN sync_status TEXT DEFAULT 'PENDING'"
                )
            }
        }
        
        val migrations = arrayOf(MIGRATION_1_2)
    }
}
```

---

#### **1.5 API Client & JWT Handling Analysis**

**Potential Issues Found:**

```kotlin
// ISSUE 1: Token stored in SharedPreferences (not encrypted)
class TokenManager {
    fun saveToken(token: String) {
        preferences.edit().putString("jwt_token", token).apply()
        // Problem: Cleartext storage, vulnerable to extraction
    }
}

// ISSUE 2: No certificate pinning
val client = OkHttpClient.Builder()
    .addInterceptor(JwtInterceptor())
    .build()
    // Problem: Vulnerable to MITM attacks

// ISSUE 3: Token expiry not validated before sending
fun addAuthHeader(request: Request): Request {
    val token = getToken()  // No expiry check here
    return request.newBuilder()
        .addHeader("Authorization", "Bearer $token")
        .build()
}
```

**Recommendations:**

✅ **Encrypted Token Storage** (Priority: HIGH)
```kotlin
// Use EncryptedSharedPreferences instead of plain SharedPreferences
val encryptedPreferences = EncryptedSharedPreferences.create(
    context,
    "secret_shared_prefs",
    MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Use in TokenManager:
fun saveToken(token: String) {
    encryptedPreferences.edit().putString("jwt_token", token).apply()
}
```

✅ **Certificate Pinning** (Priority: MEDIUM)
```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.qutykarunia.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.qutykarunia.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .addInterceptor(JwtInterceptor())
    .build()
```

✅ **Token Expiry Validation** (Priority: HIGH)
```kotlin
class JwtInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        
        // Check token expiry BEFORE sending
        if (tokenManager.isTokenExpired()) {
            // Try refresh
            return if (tokenManager.refreshToken()) {
                val newToken = tokenManager.getToken()
                request = request.newBuilder()
                    .addHeader("Authorization", "Bearer $newToken")
                    .build()
                chain.proceed(request)
            } else {
                // Redirect to login
                createUnauthorizedResponse()
            }
        } else {
            val token = tokenManager.getToken()
            request = request.newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        }
        
        return chain.proceed(request)
    }
}
```

---

### PART 2: BACKEND ANALYSIS

#### **2.1 Daily Production Endpoints Analysis**

**Issues Found:**

```python
# ISSUE 1: No input validation on daily quantity
@router.post("/daily-input")
async def record_daily_input(req: DailyInputRequest):
    # Problem: req.quantity not validated
    db.query(DailyProductionInput).create(
        spk_id=req.spk_id,
        quantity=req.quantity  # Could be -1000, 999999, etc
    )
```

**Recommendations:**

✅ **Backend Validation** (Priority: HIGH)
```python
from pydantic import BaseModel, Field, validator

class DailyInputRequest(BaseModel):
    spk_id: int
    production_date: datetime
    quantity: int = Field(..., ge=0, le=10000)  # Min 0, max 10k
    
    @validator('production_date')
    def date_not_future(cls, v):
        if v > datetime.now():
            raise ValueError('Date cannot be in the future')
        return v
    
    @validator('quantity')
    def quantity_reasonable(cls, v):
        if v == 0:
            raise ValueError('Quantity must be > 0')
        return v
```

---

#### **2.2 Approval Workflow Analysis**

**Issues Found:**

```python
# ISSUE 1: No state validation in approval flow
@router.put("/approval/{id}/approve")
async def approve_request(id: int):
    req = db.query(ApprovalRequest).get(id)
    req.status = "APPROVED"  # No check if already rejected/expired
    db.commit()
```

**Recommendations:**

✅ **State Machine for Approvals** (Priority: HIGH)
```python
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class ApprovalTransitions:
    VALID_TRANSITIONS = {
        ApprovalStatus.PENDING: [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED],
        ApprovalStatus.APPROVED: [],  # No transitions
        ApprovalStatus.REJECTED: [],  # No transitions
        ApprovalStatus.EXPIRED: [],   # No transitions
    }

@router.put("/approval/{id}/approve")
async def approve_request(id: int):
    req = db.query(ApprovalRequest).get(id)
    
    # Validate transition
    if ApprovalStatus.APPROVED not in ApprovalTransitions.VALID_TRANSITIONS.get(
        req.status, []
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve from {req.status} status"
        )
    
    # Check expiry (valid for 7 days)
    if datetime.now() - req.created_at > timedelta(days=7):
        req.status = ApprovalStatus.EXPIRED
        raise HTTPException(status_code=400, detail="Approval expired")
    
    req.status = ApprovalStatus.APPROVED
    req.approved_by = current_user.id
    req.approved_at = datetime.now()
    db.commit()
```

---

#### **2.3 Material Debt Tracking Analysis**

**Issues Found:**

```python
# ISSUE 1: Debt reconciliation not atomic
# Multiple requests could process simultaneously, causing over-reconciliation

# ISSUE 2: No audit trail for debt changes

# ISSUE 3: Debt never expires or times out
```

**Recommendations:**

✅ **Debt Reconciliation with Locking** (Priority: HIGH)
```python
@router.put("/material-debt/reconcile/{id}")
async def reconcile_debt(id: int):
    async with db.get_lock(f"debt_{id}"):  # Redis-based lock
        debt = db.query(MaterialDebt).get(id)
        
        if debt.status == "RECONCILED":
            raise HTTPException(status_code=400, detail="Already reconciled")
        
        # Atomic reconciliation
        debt.status = "RECONCILED"
        debt.reconciled_at = datetime.now()
        debt.reconciled_by = current_user.id
        
        # Create audit entry
        audit_entry = AuditLog(
            entity_type="MATERIAL_DEBT",
            entity_id=id,
            action="RECONCILED",
            old_value=json.dumps({"status": "PENDING"}),
            new_value=json.dumps({"status": "RECONCILED"}),
            changed_by=current_user.id
        )
        
        db.add(audit_entry)
        db.commit()
```

---

### PART 3: REACT FRONTEND ANALYSIS

**Issues Found:**

```typescript
// ISSUE 1: Daily input form has no debouncing on auto-save
function DailyProductionForm() {
    const [input, setInput] = useState("");
    
    useEffect(() => {
        api.saveDailyInput(input);  // Triggers on EVERY keystroke!
    }, [input]);
}

// ISSUE 2: No loading state during API calls
// User dapat submit form multiple times

// ISSUE 3: Cumulative calculation not memoized
// Recalculates on every render
```

**Recommendations:**

✅ **Debounced Auto-Save** (Priority: HIGH)
```typescript
import { debounce } from 'lodash';

function DailyProductionForm() {
    const [input, setInput] = useState("");
    const [isSaving, setIsSaving] = useState(false);
    
    const debouncedSave = useCallback(
        debounce(async (value: string) => {
            try {
                setIsSaving(true);
                await api.saveDailyInput(value);
            } finally {
                setIsSaving(false);
            }
        }, 1000),  // Wait 1 second after user stops typing
        []
    );
    
    useEffect(() => {
        debouncedSave(input);
    }, [input]);
    
    return (
        <>
            <input 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
                disabled={isSaving}
            />
            {isSaving && <Spinner />}
        </>
    );
}
```

✅ **Memoized Calculations** (Priority: MEDIUM)
```typescript
const cumulativeTotal = useMemo(
    () => calculateCumulative(dailyInputs),
    [dailyInputs]
);

const progressPercentage = useMemo(
    () => (cumulativeTotal / targetQty) * 100,
    [cumulativeTotal, targetQty]
);
```

---

## 🧪 TESTING RECOMMENDATIONS

### TESTING STRATEGY (Comprehensive)

#### **Level 1: Unit Tests (Priority: HIGHEST)**

**Files to Test:**
```
Android:
- LoginViewModel.test.kt (80+ test cases)
- DailyProductionViewModel.test.kt (100+ test cases)
- FinishGoodViewModel.test.kt (120+ test cases)
- DashboardViewModel.test.kt (60+ test cases)

Backend:
- test_approval_workflow.py (80+ test cases)
- test_material_debt.py (100+ test cases)
- test_daily_production.py (120+ test cases)
- test_barcode_processing.py (60+ test cases)

Frontend:
- DailyProductionForm.test.tsx (100+ test cases)
- FinishGoodScreen.test.tsx (120+ test cases)
- PPICDashboard.test.tsx (80+ test cases)
```

**Example Unit Test:**

```kotlin
@Test
fun testPasswordValidation() {
    val viewModel = LoginViewModel()
    
    // Too short
    val result1 = viewModel.validatePassword("123")
    assertEquals(false, result1.isValid)
    assertEquals("Password minimal 8 karakter", result1.error)
    
    // No uppercase
    val result2 = viewModel.validatePassword("password123!")
    assertEquals(false, result2.isValid)
    
    // Valid
    val result3 = viewModel.validatePassword("Password123!")
    assertEquals(true, result3.isValid)
}
```

#### **Level 2: Integration Tests (Priority: HIGH)**

**Test Scenarios:**

```
1. End-to-End Daily Production Input
   - User logs in
   - Navigates to daily production
   - Enters daily quantities for 5 days
   - System calculates cumulative correctly
   - Confirms completion
   - Backend saves all data
   - Verify database consistency

2. Offline Sync Scenario
   - User enters daily input (no network)
   - Data stored locally
   - Network comes back online
   - WorkManager syncs data
   - Backend receives all pending items
   - Local cache updated
   - No data loss

3. Barcode Scanning Workflow
   - User scans carton barcode
   - System extracts carton ID
   - Shows articles for carton
   - User confirms quantities for each article
   - Confirms carton
   - Data queued for sync (or sent if online)
   - Next carton ready

4. Approval Workflow
   - User submits SPK edit for approval
   - SPV reviews + approves
   - Manager reviews + approves
   - Executive reviews + approves
   - SPK updated in system
   - Material debt created if applicable
```

#### **Level 3: E2E Tests (Priority: MEDIUM)**

```
Tools: Appium (Android) + Selenium (Web) + Playwright

Scenarios:
1. Full production cycle: Login → Dashboard → Daily Input → Confirm → Verify
2. Barcode scanning: Scan → Count → Confirm → Next → Verify
3. Multi-user workflow: SPV approves, then Manager approves, then Exec approves
4. Offline + Sync: Work offline, reconnect, verify sync
```

#### **Level 4: Performance Tests (Priority: MEDIUM)**

```
Load Testing:
- 100 concurrent users logging in
- 500 daily production inputs
- 1000 barcode scans per hour
- API response time < 500ms (p95)

Memory/Leak Testing:
- Run app for 2 hours continuous use
- Check memory doesn't exceed 400MB
- Check no memory leaks in long-running operations
- Verify WorkManager doesn't accumulate tasks
```

---

## 🚀 STAGING ENVIRONMENT SETUP

### **Staging Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    STAGING ENVIRONMENT                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FRONTEND (Staging)                                     │
│  - URL: https://staging.erp.qutykarunia.com            │
│  - Node 18 + React 18 (production build)               │
│  - SSL/TLS certificate                                 │
│  - CORS configured for staging API                     │
│                                                         │
│  BACKEND (Staging)                                      │
│  - URL: https://api-staging.qutykarunia.com            │
│  - FastAPI + Uvicorn (replicate production)            │
│  - PostgreSQL 15 (separate DB, cloned weekly)          │
│  - Redis (separate instance)                           │
│                                                         │
│  DATABASE                                               │
│  - PostgreSQL 15                                       │
│  - 30GB storage (clone of production weekly)           │
│  - Backup daily                                        │
│  - No PII in reports/logs                              │
│                                                         │
│  MONITORING                                             │
│  - Prometheus (separate instance)                      │
│  - Grafana (staging dashboards)                        │
│  - ELK Stack (log aggregation)                         │
│                                                         │
│  LOAD BALANCER                                          │
│  - Nginx                                               │
│  - SSL termination                                     │
│  - Rate limiting (to test limits)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **Docker Compose for Staging**

```yaml
version: '3.9'

services:
  # Frontend
  frontend:
    image: erp-ui:staging
    container_name: erp-frontend-staging
    environment:
      - REACT_APP_API_URL=https://api-staging.qutykarunia.com
      - REACT_APP_ENV=staging
    ports:
      - "3001:3000"
    depends_on:
      - backend
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend
  backend:
    image: erp-backend:staging
    container_name: erp-backend-staging
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/erp_staging
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=staging_secret_key_long_string_here
      - ENVIRONMENT=staging
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: erp-postgres-staging
    environment:
      - POSTGRES_DB=erp_staging
      - POSTGRES_USER=erp_user
      - POSTGRES_PASSWORD=staging_password_here
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
      - ./backups/staging_weekly_clone.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5433:5432"
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U erp_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: erp-redis-staging
    ports:
      - "6380:6379"
    networks:
      - erp-staging
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: erp-prometheus-staging
    volumes:
      - ./prometheus-staging.yml:/etc/prometheus/prometheus.yml
      - prometheus_staging_data:/prometheus
    ports:
      - "9091:9090"
    networks:
      - erp-staging
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: erp-grafana-staging
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_staging_data:/var/lib/grafana
    ports:
      - "3003:3000"
    networks:
      - erp-staging

networks:
  erp-staging:
    driver: bridge

volumes:
  postgres_staging_data:
  prometheus_staging_data:
  grafana_staging_data:
```

### **Staging Environment Procedures**

**1. Weekly Database Clone (Friday night)**
```bash
#!/bin/bash
# Production backup → Staging database
pg_dump -h prod-db.internal -U prod_user erp_production | \
  gzip > /backups/staging_clone_$(date +%Y%m%d).sql.gz

# Restore to staging
gunzip -c /backups/staging_clone_*.sql.gz | \
  psql -h staging-db.internal -U erp_user erp_staging

# Anonymize PII
psql -h staging-db.internal -U erp_user -d erp_staging -f /scripts/anonymize_staging.sql

echo "✅ Staging database cloned and anonymized"
```

**2. Test Data Reset (Daily)**
```bash
# Clear all test data, reset to known state
psql -h staging-db.internal -U erp_user -d erp_staging -f /scripts/reset_staging.sql

# Run seed script
python /scripts/seed_staging_data.py

echo "✅ Staging test data reset"
```

**3. Smoke Testing (After each deploy)**
```bash
#!/bin/bash

# Test critical endpoints
echo "Testing authentication..."
curl -f https://api-staging.qutykarunia.com/api/auth/health || exit 1

echo "Testing production module..."
curl -f https://api-staging.qutykarunia.com/api/production/spk/list || exit 1

echo "Testing barcode endpoints..."
curl -f https://api-staging.qutykarunia.com/api/production/handshake || exit 1

echo "✅ All smoke tests passed"
```

---

## 🔄 CI/CD PIPELINE SETUP

### **Pipeline Architecture**

```
┌──────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS CI/CD                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CODE PUSH (Trigger)                                     │
│     └─→ git push origin feature/daily-production             │
│                                                              │
│  2. BUILD STAGE                                              │
│     ├─ Checkout code                                        │
│     ├─ Kotlin build (gradle)                                │
│     ├─ Python build (pip)                                   │
│     ├─ TypeScript compile (tsc)                             │
│     └─ Build Docker images                                  │
│                                                              │
│  3. TEST STAGE                                               │
│     ├─ Unit tests (90% coverage required)                   │
│     ├─ Integration tests                                    │
│     ├─ Security scan (OWASP)                                │
│     ├─ Code quality (SonarQube)                             │
│     ├─ Dependency check (for vulnerabilities)               │
│     └─ Performance baseline test                            │
│                                                              │
│  4. STAGING DEPLOY                                           │
│     ├─ Push images to registry                              │
│     ├─ Deploy to staging (docker-compose up)                │
│     ├─ Run smoke tests                                      │
│     ├─ Run E2E tests                                        │
│     └─ Send notification to QA team                         │
│                                                              │
│  5. QA APPROVAL (Manual gate)                                │
│     └─ QA team reviews + approves                           │
│                                                              │
│  6. PRODUCTION DEPLOY (if main branch)                       │
│     ├─ Tag release version                                  │
│     ├─ Push to production registry                          │
│     ├─ Blue-green deploy                                    │
│     ├─ Health check endpoints                               │
│     └─ Send notification to ops team                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### **GitHub Actions Workflow File**

```yaml
name: Build and Deploy

on:
  push:
    branches: [main, develop, staging]
  pull_request:
    branches: [main, develop]

jobs:
  # ===== BUILD JOB =====
  build:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      # Kotlin Android Build
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Build Android app
        run: |
          cd erp-ui/mobile
          ./gradlew build -x test
        env:
          ANDROID_HOME: ${{ runner.android_home }}
      
      # Backend Build
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Python dependencies
        run: |
          python -m pip install -r erp-softtoys/requirements.txt
      
      - name: Build backend
        run: |
          cd erp-softtoys
          python -m pytest --collect-only  # Verify imports
      
      # Frontend Build
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: erp-ui/frontend/package-lock.json
      
      - name: Build frontend
        run: |
          cd erp-ui/frontend
          npm ci
          npm run build
      
      # Docker images
      - name: Build Docker images
        run: |
          docker build -t erp-backend:${{ github.sha }} -f erp-softtoys/Dockerfile erp-softtoys/
          docker build -t erp-ui:${{ github.sha }} -f erp-ui/frontend/Dockerfile erp-ui/frontend/
          docker build -t erp-mobile:${{ github.sha }} -f erp-ui/mobile/app/Dockerfile erp-ui/mobile/

  # ===== TEST JOB =====
  test:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      # Unit Tests - Kotlin
      - name: Run Android unit tests
        run: |
          cd erp-ui/mobile
          ./gradlew test --info
          ./gradlew jacocoTestReport
      
      # Unit Tests - Backend
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run backend tests
        run: |
          python -m pip install -r erp-softtoys/requirements-dev.txt
          cd erp-softtoys
          pytest tests/ -v --cov=app --cov-report=xml --cov-report=term
      
      # Unit Tests - Frontend
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Run frontend tests
        run: |
          cd erp-ui/frontend
          npm ci
          npm run test -- --coverage
      
      # Code Quality
      - name: SonarQube scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      
      # Security scan
      - name: Run OWASP dependency check
        run: |
          docker run --rm -v ${{ github.workspace }}:/src \
            owasp/dependency-check --scan /src --format JSON
      
      # Performance test
      - name: Performance baseline
        run: |
          cd erp-softtoys
          locust -f locustfile.py --headless -u 100 -r 10 -t 60s

  # ===== STAGING DEPLOY =====
  deploy_staging:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop' || github.ref == 'refs/heads/staging'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Deploy to staging
        env:
          STAGING_SSH_KEY: ${{ secrets.STAGING_SSH_KEY }}
          STAGING_HOST: staging.erp.qutykarunia.com
        run: |
          mkdir -p ~/.ssh
          echo "$STAGING_SSH_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          
          ssh -i ~/.ssh/id_rsa deploy@$STAGING_HOST << 'EOF'
          cd /app/erp
          git pull origin staging
          docker-compose -f docker-compose.staging.yml down
          docker-compose -f docker-compose.staging.yml up -d
          docker-compose -f docker-compose.staging.yml exec -T backend python -m pytest tests/
          EOF
      
      - name: Smoke tests
        run: |
          bash .github/scripts/smoke_tests_staging.sh
      
      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_STAGING }}
          payload: |
            {
              "text": "✅ Staging deployment successful",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Staging Deployed*\n*Commit:* ${{ github.sha }}\n*Branch:* ${{ github.ref_name }}\n*Environment:* Staging"
                  }
                }
              ]
            }

  # ===== PRODUCTION DEPLOY (Manual approval) =====
  deploy_production:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production  # Requires manual approval
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Create release tag
        run: |
          git tag -a v${{ github.run_number }} -m "Release ${{ github.run_number }}"
          git push origin v${{ github.run_number }}
      
      - name: Deploy to production (blue-green)
        env:
          PROD_SSH_KEY: ${{ secrets.PROD_SSH_KEY }}
          PROD_HOST: api.qutykarunia.com
        run: |
          mkdir -p ~/.ssh
          echo "$PROD_SSH_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          
          ssh -i ~/.ssh/id_rsa deploy@$PROD_HOST << 'EOF'
          cd /app/erp
          
          # Blue-green deployment
          docker-compose -f docker-compose.prod.yml pull
          docker-compose -f docker-compose.prod.yml up -d --scale backend=2
          
          # Wait for new containers to be healthy
          sleep 30
          
          # Health check
          curl -f http://localhost:8000/health || exit 1
          curl -f http://localhost:3000 || exit 1
          
          # Remove old containers
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml up -d
          EOF
      
      - name: Post-deployment tests
        run: |
          bash .github/scripts/smoke_tests_prod.sh
      
      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_PROD }}
          payload: |
            {
              "text": "🚀 Production deployment successful",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Production Deployed*\n*Version:* v${{ github.run_number }}\n*Environment:* Production (Live)"
                  }
                }
              ]
            }
```

---

## 📊 MONITORING & ALERTING STRATEGY

### **Monitoring Architecture**

```
┌─────────────────────────────────────────────────────────┐
│              MONITORING STACK (ELK + Prometheus)        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  METRICS COLLECTION                                     │
│  - Prometheus (time-series database)                    │
│    ├─ API response times                               │
│    ├─ Database query times                             │
│    ├─ Barcode scan latency                             │
│    ├─ Sync success/failure rate                        │
│    └─ Mobile app crash rate                            │
│                                                         │
│  LOG AGGREGATION                                        │
│  - Elasticsearch (log storage)                         │
│  - Logstash (log shipper)                              │
│  - Kibana (visualization)                              │
│    ├─ Application logs                                │
│    ├─ API access logs                                 │
│    ├─ Database slow query logs                        │
│    └─ Error traces                                    │
│                                                         │
│  VISUALIZATION                                          │
│  - Grafana dashboards                                  │
│    ├─ System health overview                          │
│    ├─ Production workflow metrics                     │
│    ├─ Mobile app performance                          │
│    ├─ API endpoint performance                        │
│    └─ Database performance                            │
│                                                         │
│  ALERTING                                               │
│  - Alert Manager                                       │
│    ├─ Slack notifications                             │
│    ├─ PagerDuty escalation                            │
│    ├─ Email alerts                                    │
│    └─ SMS for critical issues                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **Key Metrics to Monitor**

```
┌─────────────────────────────────────────┬──────────┐
│ METRIC                                  │ THRESHOLD│
├─────────────────────────────────────────┼──────────┤
│ API Response Time (p95)                 │ < 1s     │
│ API Response Time (p99)                 │ < 2s     │
│ Error Rate (5xx)                        │ < 0.5%   │
│ Database Connection Pool Utilization    │ < 80%    │
│ Database Slow Queries (>1s)             │ < 5      │
│ Memory Usage (Backend)                  │ < 800MB  │
│ Memory Usage (Mobile)                   │ < 400MB  │
│ CPU Usage                               │ < 70%    │
│ Disk Usage                              │ < 80%    │
│ Barcode Scan Success Rate               │ > 99%    │
│ Daily Production Sync Success Rate      │ > 99.5%  │
│ Mobile App Crash Rate                   │ < 0.1%   │
│ Uptime                                  │ > 99.9%  │
│ Database Backup Success                 │ 100%     │
└─────────────────────────────────────────┴──────────┘
```

### **Prometheus Configuration**

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'erp-system'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - 'alerts.yml'

scrape_configs:
  # Backend API
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Database
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Frontend (via Google Analytics + custom)
  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend-metrics:9090']

  # Node exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### **Alert Rules**

```yaml
# alerts.yml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      # High response time
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, api_request_duration_seconds_bucket) > 1
        for: 5m
        annotations:
          summary: "High API response time"
          description: "p95 response time > 1 second"
          severity: warning

      # High error rate
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.005
        for: 2m
        annotations:
          summary: "High 5xx error rate"
          description: "Error rate > 0.5%"
          severity: critical

  - name: database_alerts
    interval: 30s
    rules:
      # Slow queries
      - alert: SlowQueries
        expr: rate(db_slow_queries_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Database slow queries"
          description: "Slow queries > 5 per minute"
          severity: warning

      # High connection pool utilization
      - alert: HighConnectionPoolUtilization
        expr: db_connection_pool_usage / db_connection_pool_max > 0.8
        for: 5m
        annotations:
          summary: "High database connection pool utilization"
          description: "Pool usage > 80%"
          severity: warning

  - name: mobile_alerts
    interval: 1m
    rules:
      # High crash rate
      - alert: MobileAppCrashRate
        expr: rate(mobile_app_crashes_total[1h]) > 0.001
        for: 5m
        annotations:
          summary: "High mobile app crash rate"
          description: "Crash rate > 0.1%"
          severity: critical

      # Sync failures
      - alert: SyncFailures
        expr: rate(sync_failures_total[5m]) > 0.01
        for: 5m
        annotations:
          summary: "High sync failure rate"
          description: "Sync failure rate > 1%"
          severity: critical

  - name: system_alerts
    interval: 30s
    rules:
      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.8
        for: 5m
        annotations:
          summary: "High memory usage"
          description: "Memory usage > 80%"
          severity: warning

      # Disk space low
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2
        for: 5m
        annotations:
          summary: "Low disk space"
          description: "Disk usage > 80%"
          severity: critical
```

### **Grafana Dashboards**

**1. System Health Dashboard**
```
┌────────────────────────────────────────┐
│ SYSTEM HEALTH OVERVIEW                 │
├────────────────────────────────────────┤
│ Uptime: 99.95%                         │
│ Active Users: 45/100                   │
│ Avg Response Time: 230ms               │
│ Error Rate: 0.2%                       │
│                                        │
│ [API Response Time Graph]              │
│ [Memory Usage Graph]                   │
│ [Disk Space Gauge]                     │
│ [Error Rate Trend]                     │
└────────────────────────────────────────┘
```

**2. Production Workflow Dashboard**
```
┌────────────────────────────────────────┐
│ PRODUCTION WORKFLOW METRICS            │
├────────────────────────────────────────┤
│ Active SPKs: 45                        │
│ Completed Today: 12                    │
│ On Track: 40 (89%)                     │
│ At Risk: 5 (11%)                       │
│                                        │
│ [Daily Output Chart]                   │
│ [Stage Distribution]                   │
│ [Quality Gate Pass Rate]               │
│ [Material Debt Tracking]               │
└────────────────────────────────────────┘
```

**3. Mobile Performance Dashboard**
```
┌────────────────────────────────────────┐
│ MOBILE APP PERFORMANCE                 │
├────────────────────────────────────────┤
│ Active Users: 12                       │
│ Avg Battery Usage: 15%/hour            │
│ Crash Rate: 0.03%                      │
│ Sync Success Rate: 99.8%               │
│                                        │
│ [Barcode Scan Latency]                │
│ [Offline Sync Queue]                  │
│ [Memory Usage]                         │
│ [Network Performance]                  │
└────────────────────────────────────────┘
```

---

## 📋 FINAL RECOMMENDATIONS

### **PRIORITY 1: CRITICAL (Do immediately)**

1. ✅ **Add Password Complexity Requirements**
   - Timeline: 1-2 hours
   - Impact: Security (prevent weak passwords)
   - Effort: Low

2. ✅ **Add 2FA Brute Force Protection**
   - Timeline: 2-3 hours
   - Impact: Security (prevent PIN guessing)
   - Effort: Medium

3. ✅ **Implement Transaction Management in Repositories**
   - Timeline: 2-3 hours
   - Impact: Data consistency
   - Effort: Medium

4. ✅ **Add Input Validation (Android + Backend)**
   - Timeline: 3-4 hours
   - Impact: Data quality
   - Effort: Medium

### **PRIORITY 2: HIGH (Do before UAT)**

5. ✅ **Implement Barcode Parsing Robustness**
   - Timeline: 1-2 hours
   - Impact: Reliability
   - Effort: Low

6. ✅ **Add Certificate Pinning**
   - Timeline: 2-3 hours
   - Impact: Security (prevent MITM)
   - Effort: Medium

7. ✅ **Encrypted Token Storage**
   - Timeline: 1-2 hours
   - Impact: Security
   - Effort: Low

8. ✅ **Unit Test Suite (90%+ coverage)**
   - Timeline: 10-12 hours
   - Impact: Quality assurance
   - Effort: High

### **PRIORITY 3: MEDIUM (Do before production)**

9. ✅ **Setup Staging Environment**
   - Timeline: 3-4 hours
   - Impact: Testing infrastructure
   - Effort: Medium

10. ✅ **Configure CI/CD Pipeline**
    - Timeline: 4-6 hours
    - Impact: Deployment automation
    - Effort: Medium

11. ✅ **Setup Monitoring & Alerts**
    - Timeline: 3-4 hours
    - Impact: Operational visibility
    - Effort: Medium

12. ✅ **Create E2E Test Suite**
    - Timeline: 8-10 hours
    - Impact: User workflow verification
    - Effort: High

### **PRIORITY 4: NICE-TO-HAVE (Post-launch improvements)**

13. Add rate limiting on API endpoints
14. Implement feature flags for gradual rollout
15. Add advanced caching strategies
16. Implement audit logging for all critical operations

---

## 📊 IMPLEMENTATION TIMELINE

```
WEEK 1 (Feb 1-5):
├─ Monday-Tuesday: Priority 1 fixes (6-8 hours)
├─ Wednesday: Unit tests (8 hours)
├─ Thursday: Staging environment setup (4 hours)
└─ Friday: CI/CD pipeline (6 hours)

WEEK 2 (Feb 8-12):
├─ Monday-Tuesday: E2E tests (10 hours)
├─ Wednesday: Monitoring setup (4 hours)
├─ Thursday: UAT preparation (4 hours)
└─ Friday: Load testing (4 hours)

WEEK 3 (Feb 15-19):
├─ Monday-Tuesday: UAT with stakeholders
├─ Wednesday: Bug fixes from UAT
├─ Thursday: Final verification
└─ Friday: Production deployment

WEEK 4+: Production support & monitoring
```

---

## ✅ RECOMMENDATION SUMMARY

### **Immediate Actions (This week)**

1. ✅ **Security Hardening** (4-6 hours)
   - Add password complexity
   - Add 2FA rate limiting
   - Encrypted token storage
   - Certificate pinning

2. ✅ **Data Validation** (3-4 hours)
   - Android input validation
   - Backend request validation
   - Error handling improvements

3. ✅ **Unit Testing** (10-12 hours)
   - Cover all ViewModels (80%+ coverage)
   - Critical backend logic
   - Frontend form logic

### **Before UAT (1-2 weeks)**

4. ✅ **Staging Environment**
   - Docker compose setup
   - Weekly database cloning
   - Smoke test suite

5. ✅ **CI/CD Pipeline**
   - GitHub Actions workflow
   - Automated testing
   - Docker image building

6. ✅ **Monitoring & Alerts**
   - Prometheus setup
   - Grafana dashboards
   - AlertManager configuration

7. ✅ **E2E Testing**
   - User workflow testing
   - Offline sync scenarios
   - Approval workflow testing

### **Production Readiness Checklist**

- [ ] All Priority 1 issues fixed
- [ ] Unit test coverage > 85%
- [ ] Staging environment verified
- [ ] CI/CD pipeline working
- [ ] Monitoring dashboards ready
- [ ] Backup & recovery tested
- [ ] Load testing passed (100 concurrent users)
- [ ] Security audit completed
- [ ] UAT sign-off received
- [ ] Runbooks created
- [ ] On-call procedures defined
- [ ] Rollback procedure tested

---

**Recommendation Status**: ✅ **COMPREHENSIVE ANALYSIS COMPLETE**

**Next Step**: Execute Priority 1 fixes this week, then proceed with staging/CI/CD setup.

**Estimated Time to Production**: 3-4 weeks with this plan

