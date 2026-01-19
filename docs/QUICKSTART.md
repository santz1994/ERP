# ⚡ QUICK START GUIDE
**Quty Karunia ERP - Start Developing in 5 Minutes**

---

## 🚀 FASTEST PATH TO DEVELOPMENT

### **Prerequisites Check (30 seconds)**
```bash
# Verify you have these installed
docker --version      # Should show 20.10+
docker-compose --version  # Should show 1.29+
git --version         # Should show 2.30+
```

If any are missing, install [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

## 🎯 START SERVICES (2 MINUTES)

### **Windows PowerShell / Command Prompt**
```bash
# Navigate to project
cd D:\Project\ERP2026

# Start everything
docker-compose up -d --build

# Wait 30 seconds for database initialization
```

### **macOS / Linux**
```bash
cd ~/Project/ERP2026
docker-compose up -d --build
```

---

## 🌐 ACCESS APPLICATIONS (1 MINUTE)

### **Bookmark These URLs**

| Service | URL | Login |
|---------|-----|-------|
| **API Docs (Swagger)** | http://localhost:8000/docs | None - Open directly |
| **API (GraphQL Explorer)** | http://localhost:8000/redoc | None - Open directly |
| **Database Admin (pgAdmin)** | http://localhost:5050 | admin@erp.local / admin |
| **Database UI (Adminer)** | http://localhost:8080 | PostgreSQL / postgres / password |
| **Monitoring (Prometheus)** | http://localhost:9090 | None - Query metrics |
| **Dashboards (Grafana)** | http://localhost:3000 | admin / admin |

---

## ✅ VERIFY EVERYTHING WORKS (1 MINUTE)

### **Test in Terminal**
```bash
# Test API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","environment":"development"}

# Check all services running
docker-compose ps

# Expected: All should show "Up"
```

### **Test in Browser**
1. Open: http://localhost:8000/docs
2. Click **"Try it out"** on any endpoint
3. Click **"Execute"**
4. Should see response

---

## 👨‍💻 START CODING (IMMEDIATELY)

### **Make Your First Change**
```bash
# 1. Edit a file (auto-reload enabled)
File: d:\Project\ERP2026\erp-softtoys\app\main.py

# 2. Change line 55:
OLD: "version": settings.API_VERSION,
NEW: "version": "2.0.0-DEV",

# 3. Save file (Ctrl+S)

# 4. Refresh browser
http://localhost:8000/

# 5. You should see the version changed instantly!
```

---

## 📋 COMMON TASKS

### **View Logs**
```bash
# All services
docker-compose logs -f

# Just the API
docker-compose logs -f backend

# Stop watching (Ctrl+C)
```

### **Access Database**
```bash
# Option A: CLI (inside container)
docker exec -it erp_postgres psql -U postgres -d erp_quty_karunia
# Then type: SELECT * FROM products;

# Option B: Web UI (pgAdmin)
# Visit: http://localhost:5050
# Login: admin@erp.local / admin
# Password: admin

# Option C: Web UI (Adminer)
# Visit: http://localhost:8080
# Select: PostgreSQL
# Server: postgres
# Username: postgres
# Password: password
```

### **Access Backend Container**
```bash
# Get bash shell
docker exec -it erp_backend bash

# Run Python command
docker exec erp_backend python -c "print('Hello')"

# View installed packages
docker exec erp_backend pip list
```

### **Restart Everything**
```bash
# Gentle restart
docker-compose restart

# Hard reset (removes data)
docker-compose down -v
docker-compose up -d --build
```

---

## 📚 NEXT STEPS

1. **Read the Docs** (5 min)
   - [Docker Setup Guide](./DOCKER_SETUP.md) - Full Docker reference
   - [Implementation Status](./IMPLEMENTATION_STATUS.md) - Current progress

2. **Explore API** (5 min)
   - Visit http://localhost:8000/docs
   - Try existing endpoints
   - Read endpoint descriptions

3. **Set Up IDE** (5 min)
   - Open: `d:\Project\ERP2026\erp-softtoys`
   - Install extensions:
     - Python (Microsoft)
     - SQLTools (Guido Kovalevsky)
     - REST Client (Huachao Mao)

4. **Start Development** (depends on task)
   - For backend: Start coding in `app/api/v1/`
   - For database: Use pgAdmin at http://localhost:5050
   - For monitoring: Check Grafana at http://localhost:3000

---

## 🆘 TROUBLESHOOTING

### **Services won't start**
```bash
# Check Docker is running
docker ps

# If error, restart Docker Desktop

# View detailed logs
docker-compose logs postgres
docker-compose logs backend

# Rebuild everything
docker-compose down -v
docker-compose up -d --build
```

### **Port already in use**
```bash
# Find what's using the port
# Windows:
netstat -ano | findstr :8000

# Kill the process (Windows):
taskkill /PID <PID_NUMBER> /F

# Or change port in docker-compose.yml:
# From: "8000:8000"
# To:   "8001:8000"
```

### **Database connection error**
```bash
# Wait 30 seconds for postgres to be ready
docker-compose logs postgres

# Should see "database system is ready to accept connections"

# If still error, rebuild database
docker-compose down -v postgres
docker-compose up -d postgres
```

### **Changes not showing**
```bash
# 1. Make sure you saved the file (Ctrl+S)
# 2. Refresh browser (F5)
# 3. Check logs for errors
docker-compose logs backend

# 4. If syntax error, fix and save again
```

---

## 📊 DEVELOPMENT WORKFLOW

### **Daily Workflow**
```bash
# 1. Start work
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f backend

# 4. Make changes to code (auto-reload)

# 5. Test via Swagger UI
# http://localhost:8000/docs

# 6. When done
docker-compose stop
```

### **When Something Breaks**
```bash
# 1. Check logs
docker-compose logs backend

# 2. Most likely: syntax error in code
# Fix and save

# 3. Still broken: database issue
docker-compose restart postgres
docker-compose restart backend

# 4. Last resort: rebuild
docker-compose down -v
docker-compose up -d --build
```

---

## 💡 PRO TIPS

### **Use Makefile (Recommended)**
```bash
# Instead of long docker-compose commands, use:
make help              # Show all available commands
make up               # Start services
make logs             # View logs
make db-shell         # Access database
make clean            # Reset everything
make format           # Format code
make test             # Run tests
```

### **Keep Terminal Window Open**
```bash
# Run in one terminal:
docker-compose logs -f

# Keep this open while developing
# You'll see all errors immediately
```

### **Use IDE Terminal**
```bash
# In VS Code:
# Terminal → New Terminal (Ctrl+`)
# Run: docker-compose logs -f backend

# Now you can code and see logs at same time
```

---

## 📞 GETTING HELP

1. **API Documentation**: http://localhost:8000/docs
2. **Setup Issues**: See [DOCKER_SETUP.md](./DOCKER_SETUP.md)
3. **Progress Tracking**: See [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md)
4. **Full Roadmap**: See [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md)

---

## ✨ YOU'RE READY!

- ✅ All services running
- ✅ Database ready
- ✅ API responding
- ✅ Docs available

**Start coding!** 🎉

```bash
# Take a look around:
curl http://localhost:8000/
curl http://localhost:8000/health

# Open Swagger UI:
http://localhost:8000/docs
```

---

**Happy Coding! 🚀**

*For full documentation, see the [docs/](.) folder*
