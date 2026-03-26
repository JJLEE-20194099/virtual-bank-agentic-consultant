#!/bin/bash

# =============================================
# Docker Data Initialization Script
# =============================================
# This script initializes sample data in running Docker containers
# Run this AFTER docker-compose up is successful

set -e  # Exit on any error

echo "🐳 Initializing sample data in Docker containers..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if containers are running
print_status "Checking if Docker containers are running..."
if ! docker-compose ps | grep -q "Up"; then
    print_error "Docker containers are not running. Please run 'docker-compose up -d' first."
    exit 1
fi

print_success "Docker containers are running."

# Wait for backend to be ready
print_status "Waiting for backend API to be ready..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8080/docs >/dev/null 2>&1; then
        print_success "Backend API is ready!"
        break
    fi

    print_status "Attempt $attempt/$max_attempts: Backend not ready yet, waiting..."
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Backend API failed to start within expected time."
    print_error "Check logs with: docker-compose logs backend"
    exit 1
fi

# Run data generation scripts
print_status "Starting data initialization..."

# 1. Generate trading data
print_status "1/5: Generating trading data..."
if docker-compose exec -T backend python /app/gen_trading_data.py; then
    print_success "✓ Trading data generated"
else
    print_error "✗ Failed to generate trading data"
    exit 1
fi

# 2. Save trading data to database
print_status "2/5: Saving trading data to database..."
if docker-compose exec -T backend python /app/save_trading_data.py; then
    print_success "✓ Trading data saved to database"
else
    print_error "✗ Failed to save trading data"
    exit 1
fi

# 3. Generate user accounts
print_status "3/5: Generating user accounts..."
if docker-compose exec -T backend python /app/gen_user_account.py; then
    print_success "✓ User accounts generated"
else
    print_error "✗ Failed to generate user accounts"
    exit 1
fi

# 4. Append stock prices
print_status "4/5: Appending stock prices..."
if docker-compose exec -T backend python /app/append_new_stock_price.py; then
    print_success "✓ Stock prices appended"
else
    print_error "✗ Failed to append stock prices"
    exit 1
fi

# 5. Calculate portfolio
print_status "5/5: Calculating portfolio..."
if docker-compose exec -T backend python /app/calculate_portfolio.py; then
    print_success "✓ Portfolio calculated"
else
    print_error "✗ Failed to calculate portfolio"
    exit 1
fi

print_success "🎉 All data initialization completed successfully!"
echo ""
echo "=================================================="
print_success "You can now access:"
echo "  📊 API Documentation: http://localhost:8080/docs"
echo "  🗄️  Database UI: http://localhost:8081"
echo "  📈 Test API: curl http://localhost:8080/api/v1/user/summary/C00001"
echo ""
print_status "To view logs: docker-compose logs -f backend"
print_status "To restart: docker-compose restart backend"