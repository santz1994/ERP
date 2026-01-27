# pgBouncer Setup for PostgreSQL 18.1-2

## Installation

```powershell
# Install pgBouncer via Chocolatey (if available)
choco install pgbouncer

# Or download from: https://www.pgbouncer.org/
```

## Configuration

pgBouncer configuration file is included: `pgbouncer.ini`

**Key Settings:**
- **Listen Port**: 6432
- **PostgreSQL Host**: localhost:5432
- **Pool Mode**: transaction
- **Max Client Connections**: 1000
- **Default Pool Size**: 25
- **Min Pool Size**: 10

## Usage

### Start pgBouncer (Windows Service or Manual)

```powershell
# Manual Start (Console)
pgbouncer -c pgbouncer.ini

# Background (using detached process)
Start-Process pgbouncer -ArgumentList "-c pgbouncer.ini" -WindowStyle Hidden

# Install as Windows Service
pgbouncer -c pgbouncer.ini --regservice install
net start pgbouncer
```

### Verify Connection

```powershell
# Via pgBouncer (port 6432)
psql -U postgres -h localhost -p 6432 -d erp_quty_karunia

# Via Direct PostgreSQL (port 5432)
psql -U postgres -h localhost -p 5432 -d erp_quty_karunia

# Via Python
python -c "import psycopg; conn = psycopg.connect('postgresql://postgres:password123@localhost:6432/erp_quty_karunia'); print('Connected via pgBouncer'); conn.close()"
```

### Monitor pgBouncer

```powershell
# Connect to pgBouncer admin console
psql -U postgres -h localhost -p 6432 -d pgbouncer

# Within admin console, useful commands:
# SHOW POOLS;
# SHOW CLIENTS;
# SHOW SERVERS;
# SHOW CONFIG;
# RELOAD;  # Reload config without restart
```

## Docker Compose Update

For future Docker setup, add to docker-compose.yml:

```yaml
pgbouncer:
  image: edoburu/pgbouncer:latest
  container_name: erp_pgbouncer
  ports:
    - "6432:6432"
  environment:
    DATABASE_URL: postgresql://postgres:password123@postgres:5432/erp_quty_karunia
    PGBOUNCER_POOL_MODE: transaction
    PGBOUNCER_MAX_CLIENT_CONN: 1000
    PGBOUNCER_DEFAULT_POOL_SIZE: 25
  depends_on:
    - postgres
  networks:
    - erp_network
```

## Troubleshooting

**Port 6432 already in use:**
```powershell
netstat -ano | findstr :6432
taskkill /PID <PID> /F
```

**Connection refused:**
- Check if PostgreSQL 18.1-2 is running on 5432
- Verify pgbouncer.ini database configuration
- Check Windows Firewall rules

**Performance tuning:**
- Adjust `default_pool_size` based on backend connections
- Monitor with `SHOW POOLS;` command
