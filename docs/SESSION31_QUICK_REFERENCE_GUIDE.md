# ⚡ QUICK REFERENCE GUIDE - SESSION 31

**Purpose**: Fast lookup for common tasks and procedures  
**Audience**: Development team, DevOps, QA  
**Updated**: January 26, 2026  

---

## 🔥 PRIORITY 1 FIXES (DO FIRST - 6-8 Hours)

### Fix 1: Password Complexity (Android + Backend)

**Android - LoginViewModel.kt**
```kotlin
fun validatePassword(password: String): Boolean {
    val hasUpperCase = password.any { it.isUpperCase() }
    val hasNumber = password.any { it.isDigit() }
    val hasSpecialChar = password.any { it in "!@#$%^&*()" }
    val isLongEnough = password.length >= 8
    
    return hasUpperCase && hasNumber && hasSpecialChar && isLongEnough
}
```

**Backend - requirements.py**
```python
@validator('password')
def password_strong(cls, v):
    if len(v) < 8:
        raise ValueError('Min 8 chars')
    if not any(c.isupper() for c in v):
        raise ValueError('Need uppercase')
    if not any(c.isdigit() for c in v):
        raise ValueError('Need digit')
    if not any(c in '!@#$%^&*()' for c in v):
        raise ValueError('Need special char')
    return v
```

### Fix 2: 2FA Rate Limiting (Backend)

```python
# erp-softtoys/app/api/routers/auth.py

from redis import Redis
from datetime import datetime, timedelta

redis = Redis()

@router.post("/2fa/confirm")
async def confirm_2fa(req: ConfirmPINRequest, user_id: int):
    # Check rate limit
    key = f"2fa_attempts:{user_id}"
    attempts = redis.get(key)
    
    if attempts and int(attempts) >= 3:
        locked_until = redis.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Locked for {locked_until}s"
        )
    
    # Verify PIN
    if verify_pin(req.pin):
        redis.delete(key)  # Clear on success
        return {"success": True}
    else:
        redis.incr(key)  # Increment on failure
        redis.expire(key, 60)  # Expire in 60 seconds
        raise HTTPException(status_code=401, detail="Invalid PIN")
```

### Fix 3: Token Encryption (Android)

```kotlin
// erp-ui/mobile/app/src/main/java/com/qutykarunia/erp/TokenManager.kt

import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class TokenManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "token_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    fun saveToken(token: String) {
        encryptedPrefs.edit().putString("jwt_token", token).apply()
    }
    
    fun getToken(): String? = encryptedPrefs.getString("jwt_token", null)
}
```

### Fix 4: Input Validation (Backend)

```python
# erp-softtoys/app/api/routers/daily_production.py

from pydantic import BaseModel, Field, validator
from datetime import datetime

class DailyInputRequest(BaseModel):
    spk_id: int
    production_date: datetime
    quantity: int = Field(..., ge=1, le=10000)  # Min 1, Max 10k
    
    @validator('production_date')
    def date_not_future(cls, v):
        if v > datetime.now():
            raise ValueError('Cannot input future date')
        return v
    
    @validator('quantity')
    def reasonable_quantity(cls, v):
        if v > 10000:
            raise ValueError('Quantity unreasonably high')
        return v
```

---

## 📋 TESTING QUICK SETUP

### Unit Test Template (Kotlin)

```kotlin
// erp-ui/mobile/app/src/test/java/LoginViewModelTest.kt

import org.junit.Test
import org.junit.Before
import org.junit.runner.RunWith
import androidx.test.ext.junit.runners.AndroidJUnit4

@RunWith(AndroidJUnit4::class)
class LoginViewModelTest {
    private lateinit var viewModel: LoginViewModel
    
    @Before
    fun setup() {
        viewModel = LoginViewModel()
    }
    
    @Test
    fun testPasswordValidation_TooShort_ReturnsFalse() {
        val result = viewModel.validatePassword("Pass1!")
        assertFalse(result)
    }
    
    @Test
    fun testPasswordValidation_NoUpperCase_ReturnsFalse() {
        val result = viewModel.validatePassword("password123!")
        assertFalse(result)
    }
    
    @Test
    fun testPasswordValidation_Valid_ReturnsTrue() {
        val result = viewModel.validatePassword("Password123!")
        assertTrue(result)
    }
}
```

### Unit Test Template (Python)

```python
# erp-softtoys/tests/test_auth.py

import pytest
from app.api.routers.auth import validate_password

class TestPasswordValidation:
    def test_too_short(self):
        with pytest.raises(ValueError):
            validate_password("Pass1!")
    
    def test_no_uppercase(self):
        with pytest.raises(ValueError):
            validate_password("password123!")
    
    def test_valid_password(self):
        assert validate_password("Password123!") is True
```

---

## 🏗️ STAGING SETUP (Quick)

### 1. Create .env File
```bash
cp .env.example .env.staging
# Edit with:
POSTGRES_DB=erp_staging
POSTGRES_USER=erp_staging_user
JWT_SECRET=$(openssl rand -base64 64)
```

### 2. Clone Database
```bash
# From production
pg_dump -h prod-db.qutykarunia.com -U prod_user erp_production | \
  gzip > backups/staging_clone.sql.gz

# To staging  
gunzip -c backups/staging_clone.sql.gz | \
  psql -h localhost -U erp_staging_user -d erp_staging
```

### 3. Start Staging
```bash
docker-compose -f docker-compose.staging.yml up -d
docker-compose -f docker-compose.staging.yml logs -f
```

### 4. Verify Health
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 🔄 CI/CD QUICK START

### 1. Add GitHub Secrets
```
Settings → Secrets → New secret
- STAGING_SSH_KEY
- STAGING_HOST: staging.erp.qutykarunia.com
- PROD_SSH_KEY
- PROD_HOST: api.erp.qutykarunia.com
```

### 2. Create Workflow File
```
.github/workflows/ci-cd.yml
(Use template from SESSION31_STAGING_CICD_IMPLEMENTATION_GUIDE.md)
```

### 3. Test Pipeline
```bash
# Push to develop branch to trigger staging deployment
git push origin develop

# Check Actions tab for progress
```

### 4. Monitor Deployment
```bash
# Check staging
curl https://staging.erp.qutykarunia.com/health

# Check logs
docker-compose -f docker-compose.staging.yml logs backend
```

---

## 📊 MONITORING QUICK START

### 1. Deploy Prometheus
```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

### 2. Deploy Grafana
```bash
docker run -d -p 3003:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:latest
```

### 3. Add Dashboard
- Datasource: Prometheus (http://prometheus:9090)
- Dashboard: Import from JSON (see docs)

### 4. Setup Alerts
```yaml
# config/alertmanager.yml
route:
  receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK'
        channel: '#erp-alerts'
```

---

## 🚀 DEPLOYMENT CHECKLIST

### Before Staging Deploy
```bash
# 1. Code quality
npm run lint
npm run build

# 2. Tests pass
npm run test -- --coverage

# 3. No uncommitted changes
git status

# 4. On correct branch
git branch

# 5. Latest commits
git log --oneline -5
```

### Deploy Command
```bash
# Staging
git push origin staging

# Production (requires approval)
git push origin main
```

### Post-Deploy Verification
```bash
# Health check
curl https://api-staging.qutykarunia.com/health

# Check logs
docker logs backend-staging --tail 50

# Run smoke tests
bash scripts/smoke-tests.sh
```

---

## 🔧 TROUBLESHOOTING

### API Service Down
```bash
# 1. Check container
docker ps | grep backend

# 2. View logs
docker logs backend --tail 100

# 3. Check resources
docker stats backend

# 4. Restart if needed
docker-compose restart backend
```

### Database Connection Error
```bash
# 1. Check database
docker ps | grep postgres

# 2. Check connection string
echo $DATABASE_URL

# 3. Test connection
psql $DATABASE_URL -c "SELECT 1"

# 4. Check pool
docker logs postgres --tail 50
```

### High Memory Usage
```bash
# Check memory
docker stats

# Check process memory
docker exec backend ps aux

# Restart service
docker-compose restart backend
```

### Deployment Failed
```bash
# Check logs
docker-compose logs backend

# Check disk space
df -h

# Check network
docker network ls

# Rebuild if needed
docker-compose down
docker-compose up --build -d
```

---

## 📞 COMMON COMMANDS

### Git
```bash
# Create feature branch
git checkout -b feature/password-validation

# Push to staging
git push origin staging

# Push to production
git push origin main

# Create backup branch
git checkout -b backup/$(date +%Y%m%d_%H%M%S)
git push origin backup/$(date +%Y%m%d_%H%M%S)
```

### Docker
```bash
# View logs
docker logs service_name --tail 50 -f

# Execute command
docker exec service_name bash

# Restart service
docker-compose restart service_name

# Rebuild image
docker-compose build --no-cache service_name

# Full restart
docker-compose down
docker-compose up -d
```

### Database
```bash
# Connect to database
psql -h localhost -U erp_staging_user -d erp_staging

# Backup database
pg_dump -U user db_name > backup.sql

# Restore database
psql -U user db_name < backup.sql

# Check slow queries
SELECT query, calls, mean_exec_time FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;
```

### Testing
```bash
# Run all tests
npm run test

# Run specific test file
npm run test -- LoginViewModel

# Run with coverage
npm run test -- --coverage

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

---

## 📈 KEY METRICS TO WATCH

```
API Response Time (p95):    < 1 second
Error Rate (5xx):           < 0.5%
Database Query Time (avg):  < 100ms
Memory Usage:               < 70%
Disk Usage:                 < 80%
Mobile App Crash Rate:      < 0.01%
Sync Success Rate:          > 99%
```

---

## 🎯 PRIORITY EXECUTION ORDER

```
Day 1-2:
1. ✅ Password validation fixes (1h)
2. ✅ 2FA rate limiting (1h)
3. ✅ Token encryption (1h)
4. ✅ Input validation (2h)
5. ✅ Unit tests (8h) - parallel

Day 3-4:
6. ✅ Staging environment setup (4h)
7. ✅ CI/CD pipeline (6h)

Day 5:
8. ✅ Monitoring setup (4h)
9. ✅ E2E tests (6h)
10. ✅ Load testing (2h)

Week 2:
11. ✅ UAT
12. ✅ Final verification
13. ✅ Production deployment
```

---

## ✨ QUICK WIN LIST

These fixes can be done in < 1 hour each:

1. ✅ Add uppercase requirement to password (10 min)
2. ✅ Add special char requirement (10 min)
3. ✅ Add number requirement (10 min)
4. ✅ Implement 2FA attempt counter (15 min)
5. ✅ Add 15-min lockout (10 min)
6. ✅ Switch to EncryptedSharedPreferences (15 min)
7. ✅ Add quantity validation (15 min)
8. ✅ Add date validation (15 min)

**Total: ~2 hours for 8 quick wins**

---

## 📖 REFERENCE DOCUMENTS

- Full analysis: `SESSION31_DEEP_TESTING_ANALYSIS_RECOMMENDATIONS.md`
- Staging/CI-CD: `SESSION31_STAGING_CICD_IMPLEMENTATION_GUIDE.md`
- Monitoring: `SESSION31_MONITORING_OBSERVABILITY_STRATEGY.md`
- Summary: `SESSION31_FINAL_SUMMARY.txt`

---

## 🆘 NEED HELP?

### For Technical Questions
- Check documentation in `/docs/` folder
- Review implementation examples in this guide
- Check GitHub Issues

### For Urgent Issues
- P1 (Critical): Page on-call engineer
- P2 (High): Slack @ backend-team
- P3 (Medium): Create GitHub issue

### For Code Review
- Create pull request with detailed description
- Link to relevant documentation
- Request review from team leads

---

**Last Updated**: January 26, 2026, 4:30 PM  
**Version**: 1.0  
**Status**: Ready for Use  

