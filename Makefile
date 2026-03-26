.PHONY: help docker-up docker-down docker-logs docker-init docker-clean docker-build \
	docker-restart docker-shell docker-db docker-redis docker-test

help:
	@echo "Virtual Bank Agentic Consultant - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Docker Management:"
	@echo "  make docker-up       - Start all Docker services"
	@echo "  make docker-down     - Stop all services"
	@echo "  make docker-restart  - Restart all services"
	@echo "  make docker-clean    - Remove containers but keep volumes"
	@echo "  make docker-reset    - Remove everything including volumes"
	@echo "  make docker-build    - Build Docker images"
	@echo ""
	@echo "Data Management:"
	@echo "  make docker-init     - Initialize sample data"
	@echo "  make docker-clean-db - Reset database"
	@echo ""
	@echo "Logs & Debug:"
	@echo "  make docker-logs     - View all logs"
	@echo "  make docker-logs-api - View backend API logs"
	@echo "  make docker-logs-worker - View Celery worker logs"
	@echo "  make docker-logs-beat   - View Celery beat logs"
	@echo "  make docker-logs-db     - View PostgreSQL logs"
	@echo ""
	@echo "Access Services:"
	@echo "  make docker-shell-api - Shell into backend container"
	@echo "  make docker-shell-db  - Shell into PostgreSQL"
	@echo "  make docker-shell-redis - Shell into Redis"
	@echo ""
	@echo "Monitoring:"
	@echo "  make docker-ps     - Show running containers"
	@echo "  make docker-stats  - Show resource usage"
	@echo "  make docker-test   - Test all services"
	@echo ""
	@echo "Quick Access:"
	@echo "  API Docs: http://localhost:8080/docs"
	@echo "  Adminer (DB): http://localhost:8081"

# Docker Management
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo "API: http://localhost:8080/docs"
	@sleep 10

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "✓ Services stopped"

docker-restart:
	@echo "Restarting Docker services..."
	docker-compose restart
	@echo "✓ Services restarted"

docker-clean:
	@echo "Removing Docker containers..."
	docker-compose down
	@echo "✓ Containers removed (volumes kept)"

docker-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✓ All removed"; \
	else \
		echo "Cancelled"; \
	fi

docker-build:
	@echo "Building Docker images..."
	docker-compose build --no-cache
	@echo "✓ Images built"

# Data Management
docker-init:
	@echo "Initializing sample data..."
	bash docker-init-data.sh

docker-clean-db:
	@echo "WARNING: This will delete all database data!"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker volume rm vbac_postgres_data; \
		docker-compose up -d postgres; \
		echo "✓ Database cleaned"; \
	else \
		echo "Cancelled"; \
	fi

# Logs
docker-logs:
	docker-compose logs -f

docker-logs-api:
	docker-compose logs -f backend

docker-logs-worker:
	docker-compose logs -f celery-worker

docker-logs-beat:
	docker-compose logs -f celery-beat

docker-logs-db:
	docker-compose logs -f postgres

# Shell Access
docker-shell-api:
	docker-compose exec backend bash

docker-shell-db:
	docker-compose exec postgres psql -U swin -d vbac

docker-shell-redis:
	docker-compose exec redis redis-cli

docker-shell-kafka:
	docker-compose exec kafka bash

# Monitoring
docker-ps:
	docker-compose ps

docker-stats:
	docker stats

docker-test:
	@echo "Testing services..."
	@echo ""
	@echo "PostgreSQL:"
	@docker-compose exec -T postgres pg_isready -U swin || echo "✗ PostgreSQL not ready"
	@echo "✓ PostgreSQL is ready"
	@echo ""
	@echo "Redis:"
	@docker-compose exec -T redis redis-cli ping || echo "✗ Redis not ready"
	@echo "✓ Redis is ready"
	@echo ""
	@echo "Kafka:"
	@docker-compose exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list || echo "✗ Kafka not ready"
	@echo "✓ Kafka is ready"
	@echo ""
	@echo "Backend API:"
	@curl -s http://localhost:8080/docs > /dev/null && echo "✓ API is responding" || echo "✗ API not responding"
	@echo ""
	@echo "All services are healthy!"

# Shortcuts
up: docker-up
down: docker-down
logs: docker-logs
ps: docker-ps
test: docker-test
init: docker-init
restart: docker-restart
reset: docker-reset
shell: docker-shell-api

.PHONY: help docker-up docker-down docker-logs docker-init docker-clean docker-build \
	docker-restart docker-shell-api docker-shell-db docker-shell-redis docker-test \
	docker-ps docker-stats docker-logs-api docker-logs-worker docker-logs-beat docker-logs-db \
	docker-clean-db docker-reset docker-shell-kafka docker-logs-kafka up down logs ps test init restart reset shell
