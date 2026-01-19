# Makefile for Quty Karunia ERP System
# Convenient commands for development and deployment

.PHONY: help build up down restart logs shell db-shell test lint format clean

# Default target
help:
	@echo "Quty Karunia ERP System - Available Commands"
	@echo ""
	@echo "  Development:"
	@echo "    make up              - Start all services"
	@echo "    make down            - Stop all services"
	@echo "    make restart         - Restart all services"
	@echo "    make build           - Build Docker images"
	@echo "    make logs            - View logs for all services"
	@echo "    make logs-backend    - View backend logs only"
	@echo ""
	@echo "  Database:"
	@echo "    make db-shell        - Access PostgreSQL shell"
	@echo "    make db-migrate      - Run database migrations"
	@echo "    make db-seed         - Seed test data"
	@echo "    make db-backup       - Backup database to SQL file"
	@echo "    make db-restore      - Restore database from backup"
	@echo ""
	@echo "  Code Quality:"
	@echo "    make format          - Format code with Black"
	@echo "    make lint            - Run Flake8 linter"
	@echo "    make type-check      - Run MyPy type checker"
	@echo "    make test            - Run pytest tests"
	@echo "    make test-cov        - Run tests with coverage"
	@echo ""
	@echo "  API:"
	@echo "    make shell           - Access backend container shell"
	@echo "    make api-docs        - Open Swagger UI (localhost:8000/docs)"
	@echo ""
	@echo "  Utility:"
	@echo "    make clean           - Remove all containers and volumes"
	@echo "    make status          - Show service status"
	@echo "    make health-check    - Test all services"
	@echo ""

# ============================================================================
# DEVELOPMENT COMMANDS
# ============================================================================

up:
	docker-compose up -d
	@echo "✅ All services started. Check status with: make status"

down:
	docker-compose down
	@echo "✅ All services stopped"

restart:
	docker-compose restart
	@echo "✅ All services restarted"

build:
	docker-compose build
	@echo "✅ Docker images built"

rebuild:
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d
	@echo "✅ Full rebuild complete"

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-postgres:
	docker-compose logs -f postgres

logs-redis:
	docker-compose logs -f redis

status:
	docker-compose ps

health-check:
	@echo "Checking PostgreSQL..."
	@docker exec erp_postgres pg_isready -U postgres
	@echo "Checking Redis..."
	@docker exec erp_redis redis-cli ping
	@echo "Checking Backend..."
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo "✅ All health checks passed"

# ============================================================================
# DATABASE COMMANDS
# ============================================================================

db-shell:
	docker exec -it erp_postgres psql -U postgres -d erp_quty_karunia

db-migrate:
	docker exec erp_backend alembic upgrade head

db-seed:
	docker exec erp_backend python seed_data.py

db-backup:
	docker exec erp_postgres pg_dump -U postgres erp_quty_karunia > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Database backed up"

db-restore:
	@read -p "Enter backup file name: " backup; \
	docker exec -i erp_postgres psql -U postgres erp_quty_karunia < $$backup
	@echo "✅ Database restored"

db-reset:
	docker-compose down -v
	docker-compose up -d postgres
	@sleep 30
	docker-compose up -d backend
	@echo "✅ Database reset and ready"

db-logs:
	docker-compose logs postgres

# ============================================================================
# CODE QUALITY & TESTING
# ============================================================================

format:
	docker exec erp_backend black app/

lint:
	docker exec erp_backend flake8 app/ --max-line-length=88

type-check:
	docker exec erp_backend mypy app/ --ignore-missing-imports

test:
	docker exec erp_backend pytest tests/ -v

test-cov:
	docker exec erp_backend pytest tests/ --cov=app --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

test-specific:
	@read -p "Enter test file/name: " test; \
	docker exec erp_backend pytest $$test -v

quality: format lint type-check
	@echo "✅ Code quality checks complete"

# ============================================================================
# API & SHELL ACCESS
# ============================================================================

shell:
	docker exec -it erp_backend bash

api-docs:
	@echo "Opening API documentation at http://localhost:8000/docs"
	@start http://localhost:8000/docs || xdg-open http://localhost:8000/docs || open http://localhost:8000/docs

pgadmin:
	@echo "Opening pgAdmin at http://localhost:5050"
	@start http://localhost:5050 || xdg-open http://localhost:5050 || open http://localhost:5050

grafana:
	@echo "Opening Grafana at http://localhost:3000"
	@start http://localhost:3000 || xdg-open http://localhost:3000 || open http://localhost:3000

prometheus:
	@echo "Opening Prometheus at http://localhost:9090"
	@start http://localhost:9090 || xdg-open http://localhost:9090 || open http://localhost:9090

# ============================================================================
# MAINTENANCE & CLEANUP
# ============================================================================

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

clean-logs:
	docker container prune -f
	docker image prune -f
	@echo "✅ Docker logs and unused resources cleaned"

clean-volumes:
	docker volume prune -f
	@echo "✅ Unused volumes removed"

# ============================================================================
# DOCKER OPERATIONS
# ============================================================================

docker-stats:
	docker stats

docker-prune:
	docker system prune -a --volumes -f
	@echo "✅ All unused Docker resources removed"

# ============================================================================
# DEVELOPMENT SETUP
# ============================================================================

init:
	cp erp-softtoys/.env.example erp-softtoys/.env
	make build
	make up
	make db-migrate
	@echo "✅ Initial setup complete. Frontend ready at localhost:8000"

dev:
	make up
	make logs

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

deploy-prod:
	@echo "⚠️  Production deployment checklist:"
	@echo "  1. Update .env with production values"
	@echo "  2. Build production images: docker-compose -f docker-compose.prod.yml build"
	@echo "  3. Deploy: docker stack deploy -c docker-compose.prod.yml erp"

# ============================================================================
# INFO & HELP
# ============================================================================

info:
	@echo "Quty Karunia ERP System - Project Information"
	@echo ""
	@docker --version
	@docker-compose --version
	@echo ""
	@echo "Services:"
	@docker-compose config --services
	@echo ""
	@echo "For more help, run: make help"

version:
	@echo "Quty Karunia ERP v2.0.0"
	@docker exec erp_backend python -c "import app; print(f'API Version: 2.0.0')"

# Phony targets
.PHONY: all help up down restart build logs shell test format lint clean
