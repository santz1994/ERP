#!/bin/bash

##############################################################################
# Quty Karunia ERP - Production Deployment Script
# Deploys all services with SSL/TLS, monitoring, and logging
# Usage: ./deploy.sh [environment] [action]
# Examples:
#   ./deploy.sh production start
#   ./deploy.sh production restart
#   ./deploy.sh production stop
#   ./deploy.sh production status
##############################################################################

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
ACTION=${2:-start}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
BACKUP_DIR="/backups/erp"
LOG_FILE="$PROJECT_DIR/deployment-$(date +%Y%m%d_%H%M%S).log"

##############################################################################
# Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║ $1"
    echo "╚════════════════════════════════════════════════════════════════╝"
}

##############################################################################
# Pre-flight Checks
##############################################################################

check_prerequisites() {
    print_header "Pre-Flight Checks"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "✓ Docker installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "✓ Docker Compose installed"
    
    # Check .env file
    if [ ! -f "$PROJECT_DIR/.env.${ENVIRONMENT}" ]; then
        log_error ".env.${ENVIRONMENT} file not found"
        echo "Create $PROJECT_DIR/.env.${ENVIRONMENT} with required variables"
        exit 1
    fi
    log_success "✓ Environment file (.env.${ENVIRONMENT}) found"
    
    # Check docker-compose file
    COMPOSE_FILE="$PROJECT_DIR/docker-compose.${ENVIRONMENT}.yml"
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "docker-compose.${ENVIRONMENT}.yml not found"
        exit 1
    fi
    log_success "✓ Docker Compose file found"
    
    # Check backup directory
    if [ "$ACTION" != "stop" ]; then
        if [ ! -d "$BACKUP_DIR" ]; then
            log_info "Creating backup directory: $BACKUP_DIR"
            mkdir -p "$BACKUP_DIR"
            chmod 750 "$BACKUP_DIR"
        fi
        log_success "✓ Backup directory ready"
    fi
}

##############################################################################
# SSL/TLS Setup
##############################################################################

setup_ssl() {
    print_header "Setting up SSL/TLS Certificates"
    
    local CERT_DIR="$PROJECT_DIR/certbot/conf"
    local DOMAIN="erp.qutykarunia.com"
    
    # Create directories
    mkdir -p "$CERT_DIR/live/$DOMAIN"
    mkdir -p "$PROJECT_DIR/certbot/www"
    
    # Check if certificate already exists
    if [ -f "$CERT_DIR/live/$DOMAIN/fullchain.pem" ]; then
        log_success "✓ SSL certificate already installed"
        return 0
    fi
    
    log_info "Generating SSL certificate for $DOMAIN..."
    
    # Option 1: Use existing Let's Encrypt certificate (if in production)
    if [ "$ENVIRONMENT" = "production" ]; then
        log_warning "⚠ For production, please manually setup Let's Encrypt certificate:"
        echo "   docker-compose -f $COMPOSE_FILE run --rm certbot certonly --standalone \\"
        echo "     -d $DOMAIN \\"
        echo "     --email admin@qutykarunia.com \\"
        echo "     --agree-tos \\"
        echo "     --non-interactive"
        return 0
    fi
    
    # Option 2: Generate self-signed certificate for development
    log_info "Generating self-signed certificate for development..."
    
    openssl req -x509 -newkey rsa:4096 -nodes \
        -out "$CERT_DIR/live/$DOMAIN/fullchain.pem" \
        -keyout "$CERT_DIR/live/$DOMAIN/privkey.pem" \
        -days 365 \
        -subj "/C=ID/ST=Java/L=Bandung/O=Quty Karunia/CN=$DOMAIN"
    
    cp "$CERT_DIR/live/$DOMAIN/fullchain.pem" "$CERT_DIR/live/$DOMAIN/chain.pem"
    
    log_success "✓ Self-signed certificate created"
}

##############################################################################
# Database Setup & Migration
##############################################################################

setup_database() {
    print_header "Database Setup & Migration"
    
    log_info "Pulling latest database image..."
    docker-compose -f "$COMPOSE_FILE" pull postgres
    
    log_info "Starting PostgreSQL..."
    docker-compose -f "$COMPOSE_FILE" up -d postgres
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to become ready (max 30 seconds)..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres &> /dev/null; then
            log_success "✓ PostgreSQL is ready"
            break
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "PostgreSQL failed to start in time"
        return 1
    fi
    
    log_info "Running database migrations..."
    docker-compose -f "$COMPOSE_FILE" run --rm backend alembic upgrade head
    
    log_success "✓ Database setup complete"
}

##############################################################################
# Service Startup
##############################################################################

start_services() {
    print_header "Starting Services"
    
    # Load environment
    export $(cat "$PROJECT_DIR/.env.${ENVIRONMENT}" | grep -v '^#' | xargs)
    
    log_info "Starting all services (docker-compose up -d)..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for critical services
    log_info "Waiting for services to be healthy..."
    
    local services=("postgres" "redis" "backend" "nginx")
    for service in "${services[@]}"; do
        log_info "  Waiting for $service..."
        docker-compose -f "$COMPOSE_FILE" up -d $service
        sleep 2
    done
    
    sleep 3
    log_success "✓ Services started"
}

##############################################################################
# Health Checks
##############################################################################

health_check() {
    print_header "Health Checks"
    
    local all_healthy=true
    
    # Check PostgreSQL
    if docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres &> /dev/null; then
        log_success "✓ PostgreSQL is healthy"
    else
        log_error "✗ PostgreSQL is not responding"
        all_healthy=false
    fi
    
    # Check Redis
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping &> /dev/null; then
        log_success "✓ Redis is healthy"
    else
        log_error "✗ Redis is not responding"
        all_healthy=false
    fi
    
    # Check Backend API
    if curl -s -f http://localhost:8000/health &> /dev/null; then
        log_success "✓ Backend API is healthy"
    else
        log_warning "⚠ Backend API not yet responding (may still be starting)"
    fi
    
    # Check Prometheus
    if curl -s -f http://localhost:9090/-/healthy &> /dev/null; then
        log_success "✓ Prometheus is healthy"
    else
        log_warning "⚠ Prometheus not ready"
    fi
    
    if [ "$all_healthy" = false ]; then
        log_error "Some services are not healthy. Check logs: docker-compose logs"
        return 1
    fi
    
    log_success "✓ All critical services are healthy"
}

##############################################################################
# Status Check
##############################################################################

status_check() {
    print_header "Service Status"
    
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

##############################################################################
# Logs
##############################################################################

show_logs() {
    print_header "Recent Logs"
    
    local service=${1:-backend}
    log_info "Showing logs for $service (last 50 lines):"
    echo ""
    docker-compose -f "$COMPOSE_FILE" logs --tail=50 "$service"
}

##############################################################################
# Backup
##############################################################################

create_backup() {
    print_header "Creating Database Backup"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_DIR/erp_backup_$timestamp.sql.gz"
    
    log_info "Backing up database to $backup_file..."
    
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump \
        -U postgres \
        erp_quty_karunia_production | gzip > "$backup_file"
    
    if [ -f "$backup_file" ]; then
        log_success "✓ Backup created: $backup_file"
        
        # Keep only last 7 days
        log_info "Cleaning old backups (> 7 days)..."
        find "$BACKUP_DIR" -name "erp_backup_*.sql.gz" -mtime +7 -delete
        
        log_success "✓ Backup complete"
    else
        log_error "✗ Backup failed"
        return 1
    fi
}

##############################################################################
# Main Actions
##############################################################################

action_start() {
    check_prerequisites
    setup_ssl
    setup_database
    start_services
    sleep 5
    health_check
    
    print_header "Deployment Successful! 🎉"
    echo ""
    log_success "Environment: $ENVIRONMENT"
    log_success "Services Started:"
    echo "  • API: http://localhost:8000"
    echo "  • Swagger UI: http://localhost:8000/docs"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3000"
    echo "  • pgAdmin: http://localhost:5050"
    echo ""
    log_info "View logs: docker-compose -f $COMPOSE_FILE logs -f backend"
}

action_stop() {
    print_header "Stopping Services"
    log_info "Stopping all services..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "✓ All services stopped"
}

action_restart() {
    action_stop
    sleep 2
    action_start
}

action_status() {
    status_check
}

action_logs() {
    show_logs "${3:-backend}"
}

action_backup() {
    create_backup
}

##############################################################################
# Main Entry Point
##############################################################################

main() {
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║ Quty Karunia ERP - Production Deployment Script                 ║"
    echo "║ Environment: $ENVIRONMENT"
    echo "║ Action: $ACTION"
    echo "║ Log: $LOG_FILE"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    case "$ACTION" in
        start)
            action_start
            ;;
        stop)
            action_stop
            ;;
        restart)
            action_restart
            ;;
        status)
            action_status
            ;;
        logs)
            action_logs "$@"
            ;;
        backup)
            action_backup
            ;;
        *)
            log_error "Unknown action: $ACTION"
            echo ""
            echo "Usage: $0 [environment] [action]"
            echo ""
            echo "Environments: production, staging, development"
            echo "Actions:"
            echo "  start      - Start all services"
            echo "  stop       - Stop all services"
            echo "  restart    - Restart all services"
            echo "  status     - Show service status"
            echo "  logs       - Show service logs"
            echo "  backup     - Create database backup"
            echo ""
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

