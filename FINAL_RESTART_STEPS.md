# 🔄 FINAL RESTART INSTRUCTION

## ⚠️ MASALAH
Backend sepertinya belum load semua file yang sudah di-update.

## ✅ SOLUSI

### Step 1: HARD STOP Backend
Tekan **CTRL+C** 2x di terminal backend (force stop)

### Step 2: Clear Python Cache
```powershell
cd d:\Project\ERP2026\erp-softtoys
Remove-Item -Recurse -Force __pycache__, app/__pycache__, app/**/__pycache__ -ErrorAction SilentlyContinue
```

### Step 3: Start Backend Fresh
```powershell
# MAKE SURE YOU'RE IN erp-softtoys DIRECTORY!
cd d:\Project\ERP2026\erp-softtoys
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Verify Clean Start
Output harus:
```
INFO:     Application startup complete.
```

❌ TIDAK ADA error tentang SPKMaterialAllocation!

### Step 5: Test Work Orders Endpoint
```powershell
# Di terminal baru
$token = "eyJhbGc..." # (dari login)
$headers = @{"Authorization" = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/work-orders/" -Headers $headers
```

Jika sukses, akan return array work orders (bisa empty [])

### Step 6: Hard Refresh Browser
- Buka http://localhost:5173
- Tekan CTRL+SHIFT+R
- Login: admin / admin123

## 📊 Expected Result
✅ No CORS errors
✅ Work orders endpoint returns 200 OK
✅ Dashboard loads without crash

---

**Jalankan Step 1-3 sekarang!**
