#!/bin/bash

# =============================================
# Docker Startup & Initialization Automation
# =============================================
# This script automates the entire startup process:
# 1. Start docker-compose services
# 2. Wait for backend to be healthy
# 3. Run data initialization
# 4. Restart celery-worker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${MAGENTA}===============================================${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}===============================================${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================
# STEP 1: Start Docker Compose
# =============================================
print_header "STEP 1: Starting Docker Compose Services"

print_info "Bringing up containers (this may take a moment)..."
docker-compose up -d

# Check if Kafka started successfully
print_info "Checking if all critical services are running..."
sleep 10  # Give services time to start

if docker-compose ps | grep -q "vbac-kafka.*Exited"; then
    print_error "❌ Kafka container failed to start!"
    print_error "Check logs with: docker-compose logs vbac-kafka"
    print_error "Common fix: Run 'docker-compose down -v' to remove volumes and try again"
    exit 1
fi

if docker-compose ps | grep -q "unhealthy"; then
    print_warning "⚠️  Some services are unhealthy:"
    docker-compose ps | grep -i unhealthy
    print_error "Please check the logs and try again"
    exit 1
fi

docker restart vbac-kafka

print_success "Docker compose started successfully"
echo ""

# =============================================
# STEP 2: Wait for Backend to be Ready
# =============================================
print_header "STEP 2: Waiting for Backend to be Ready"

max_attempts=60  # 5 minutes (60 * 5 seconds)
attempt=1

print_info "Backend healthcheck start_period: 40s"
print_info "Total timeout: ~300 seconds"
echo ""

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8080/docs >/dev/null 2>&1; then
        print_success "Backend API is ready!"
        break
    fi

    elapsed=$((attempt * 5))
    print_info "Attempt $attempt/$max_attempts ($elapsed seconds): Backend not ready yet..."
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Backend API failed to start within expected time"
    print_error "Check logs with: docker-compose logs backend"
    exit 1
fi

echo ""

# =============================================
# STEP 3: Optional - Restart Backend
# =============================================
print_header "STEP 3: Restarting Backend (Optional - for clean state)"

read -p "Do you want to restart backend? (y/n) " -n 1 -r restart_backend
echo
if [[ $restart_backend =~ ^[Yy]$ ]]; then
    print_info "Restarting backend..."
    docker restart vbac-backend
    
    # Wait again for backend after restart
    print_info "Waiting for backend to be ready again..."
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8080/docs >/dev/null 2>&1; then
            print_success "Backend API is ready!"
            break
        fi
        print_info "Attempt $attempt/$max_attempts: Backend not ready yet..."
        sleep 5
        attempt=$((attempt + 1))
    done
else
    print_info "Skipping backend restart"
fi

echo ""

# =============================================
# STEP 4: Run Data Initialization
# =============================================
print_header "STEP 4: Running Data Initialization"

# Execute docker-init-data.sh
if [ -f "./docker-init-data.sh" ]; then
    print_info "Executing docker-init-data.sh..."
    bash ./docker-init-data.sh
    
    if [ $? -ne 0 ]; then
        print_error "Data initialization failed"
        exit 1
    fi
else
    print_error "docker-init-data.sh not found in current directory"
    exit 1
fi

echo ""

# =============================================
# STEP 5: Restart Celery Worker
# =============================================
print_header "STEP 5: Restarting Celery Worker"

print_info "Restarting celery-worker..."
docker restart vbac-celery-worker

# Wait a bit for celery to start
sleep 5

# Check if celery worker is running
if docker-compose ps | grep -q "vbac-celery-worker.*Up"; then
    print_success "Celery worker is running!"
else
    print_warning "Celery worker status unknown, check logs with: docker-compose logs celery-worker"
fi

echo ""

# =============================================
# Completion Summary
# =============================================
print_header "✅ Startup Complete!"

echo ""
echo -e "${GREEN}Available endpoints:${NC}"
echo "  📊 API Documentation: http://localhost:8080/docs"
echo "  🗄️  Database UI:        http://localhost:8081"
echo "  ⚙️  Redis:              localhost:6379"
echo ""
echo -e "${GREEN}Useful commands:${NC}"
echo "  View all logs:     ${BLUE}docker-compose logs -f${NC}"
echo "  View backend logs: ${BLUE}docker-compose logs -f backend${NC}"
echo "  View celery logs:  ${BLUE}docker-compose logs -f celery-worker${NC}"
echo "  Stop all:          ${BLUE}docker-compose down${NC}"
echo ""
