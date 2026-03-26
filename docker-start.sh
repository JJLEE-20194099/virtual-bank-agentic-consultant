#!/bin/bash

# Virtual Bank Agentic Consultant - Docker Setup & Data Initialization
# This script starts all Docker services and initializes data

set -e

PROJECT_DIR="/root/code/hackathon/virtual-bank-agentic-consultant"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║  Virtual Bank Agentic Consultant - Docker Setup              ║
║                                                               ║
║  This will start all Docker services:                         ║
║  - PostgreSQL Database                                        ║
║  - Redis Cache                                                ║
║  - Apache Kafka                                               ║
║  - Adminer (DB UI)                                            ║
║  - Backend API                                                ║
║  - Celery Worker                                              ║
║  - Celery Beat                                                ║
║                                                               ║
║  Then initialize data:                                        ║
║  - Generate trading data                                      ║
║  - Save to database                                           ║
║  - Create users                                               ║
║  - Update stock prices                                        ║
║  - Calculate portfolios                                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

cd "$PROJECT_DIR"

log "Starting Docker services..."
docker-compose up -d

log "Waiting for services to be healthy..."
sleep 15

# Check services
log "Verifying services are running..."

if docker-compose ps | grep -q "postgres.*healthy"; then
    log_success "PostgreSQL is healthy"
else
    log_error "PostgreSQL is not healthy"
    log_warning "Check logs: docker-compose logs postgres"
fi

if docker-compose ps | grep -q "redis.*healthy"; then
    log_success "Redis is healthy"
else
    log_error "Redis is not healthy"
    log_warning "Check logs: docker-compose logs redis"
fi

if docker-compose ps | grep -q "backend.*healthy"; then
    log_success "Backend API is healthy"
else
    log_error "Backend API is not healthy"
    log_warning "Check logs: docker-compose logs backend"
fi

echo ""
log "All Docker services started!"
echo ""

log "Services accessible at:"
log "  Backend API: http://localhost:8080"
log "  Swagger UI: http://localhost:8080/docs"
log "  Adminer (PostgreSQL): http://localhost:8081"
log "  PostgreSQL: localhost:5432"
log "  Redis: localhost:6379"
log "  Kafka: localhost:9092"

echo ""
log "Next steps:"
log "  1. Initialize data: bash docker-init-data.sh"
log "  2. View logs: docker-compose logs -f backend"
log "  3. Stop services: docker-compose down"
log "  4. Access http://localhost:8080/docs"

echo ""
log_success "Docker setup complete!"
