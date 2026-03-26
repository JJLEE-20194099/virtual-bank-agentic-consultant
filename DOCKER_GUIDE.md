# Docker Setup Guide

Complete Docker setup for Virtual Bank Agentic Consultant with all services.

## 📦 What's Included

```
docker-compose.yml    → Orchestrates all services
Dockerfile           → Container image for backend
.dockerignore       → Files to exclude from Docker build
docker-start.sh     → Start all services
docker-init-data.sh → Initialize database with sample data
```

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start all Docker services
bash docker-start.sh

# 2. Initialize sample data
bash docker-init-data.sh

# 3. Access API
open http://localhost:8080/docs
```

---

## 📋 Services Included

### 1. **PostgreSQL** (Port 5432)
- Database for transactions, portfolios, users
- Credentials: `swin` / `swin`
- Database: `vbac`
- Volume: `postgres_data` (persistent)

### 2. **Redis** (Port 6379)
- Cache for realtime prices
- Session storage
- Celery broker
- Volume: `redis_data` (persistent)

### 3. **Apache Kafka** (Port 9092)
- Event streaming
- Message queues for async processing
- Topics: conversation.transcript, conversation.nlp, etc.

### 4. **Zookeeper** (Port 2181)
- Kafka coordinator
- Service discovery

### 5. **Adminer** (Port 8081)
- Web UI for PostgreSQL
- Access: http://localhost:8081
- System: PostgreSQL
- Server: postgres
- User: swin
- Password: swin
- Database: vbac

### 6. **Backend API** (Port 8080)
- FastAPI server
- Swagger UI: http://localhost:8080/docs
- OpenAPI: http://localhost:8080/api/v1
- Volume mounted for development (auto-reload)

### 7. **Celery Worker**
- Background task processing
- Queues: portfolio, recommend, realtime_price
- Concurrency: 4 workers
- Processes: portfolio calculations, recommendations, price updates

### 8. **Celery Beat**
- Scheduled task scheduler
- Runs periodic jobs
- Configuration in `/backend/tasks.py`

---

## 🐳 Docker Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network (vbac-network)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ PostgreSQL │  │   Redis    │  │   Kafka    │       │
│  │  :5432     │  │   :6379    │  │   :9092    │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         ↓              ↓                ↓              │
│  ┌─────────────────────────────────────────┐           │
│  │         Backend API (FastAPI)            │           │
│  │  http://localhost:8080/docs             │           │
│  └─────────────────────────────────────────┘           │
│         ↓              ↓                                │
│  ┌────────────┐  ┌────────────┐                        │
│  │   Celery   │  │   Celery   │                        │
│  │   Worker   │  │    Beat    │                        │
│  └────────────┘  └────────────┘                        │
│                                                         │
│  ┌────────────┐                                        │
│  │  Adminer   │  http://localhost:8081                │
│  │  (Zookeeper)                                        │
│  └────────────┘                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Usage Commands

### Start Services

```bash
# Start all services in background
bash docker-start.sh

# Or with docker-compose directly
docker-compose up -d

# View logs in real-time
docker-compose logs -f
```

### Initialize Data

```bash
# Run all data initialization scripts
bash docker-init-data.sh

# Or manually:
docker-compose exec backend python gen_trading_data.py
docker-compose exec backend python save_trading_data.py
docker-compose exec backend python gen_user_account.py
docker-compose exec backend python append_new_stock_price.py
docker-compose exec backend python calculate_portfolio.py
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f kafka

# Real-time logs (last 100 lines)
docker-compose logs --tail=100 -f backend
```

### Manage Services

```bash
# View status
docker-compose ps

# Stop all services
docker-compose stop

# Start stopped services
docker-compose start

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Remove containers (keeps volumes)
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

### Execute Commands Inside Containers

```bash
# Run Python script
docker-compose exec backend python gen_trading_data.py

# Access Python shell
docker-compose exec backend python

# Access PostgreSQL
docker-compose exec postgres psql -U swin -d vbac

# Access Redis CLI
docker-compose exec redis redis-cli

# Access Kafka
docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check Celery tasks
docker-compose exec celery-worker celery -A backend.tasks inspect active
```

---

## 🔧 Environment Variables

### Backend

Automatically set from docker-compose:
```
DATABASE_URL=postgresql://swin:swin@postgres:5432/vbac
REDIS_URL=redis://redis:6379/0
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### Celery

```
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

### From .env file

Copy your API keys to `.env`:
```bash
cp .env.example .env
# Edit .env with your keys
```

---

## 🌐 Access Services

| Service | URL/Address | Credentials |
|---------|------------|-------------|
| **API Docs** | http://localhost:8080/docs | - |
| **API Base** | http://localhost:8080/api/v1 | - |
| **Adminer** | http://localhost:8081 | swin/swin |
| **PostgreSQL** | localhost:5432 | swin/swin |
| **Redis** | localhost:6379 | - |
| **Kafka** | localhost:9092 | - |

### Example API Calls

```bash
# Get user portfolio
curl http://localhost:8080/api/v1/user/summary/C00001

# Get market data
curl "http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=30&interval=1d"

# Get company info
curl http://localhost:8080/api/v1/company/info/FPT

# Chat with AI
curl -X POST http://localhost:8080/api/v1/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"C00001","message":"Danh mục của tôi thế nào?"}'
```

---

## 🛠️ Troubleshooting

### Service Won't Start

```bash
# Check if port is already in use
lsof -i :8080  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Force remove container
docker-compose rm -f backend

# Rebuild image
docker-compose build --no-cache backend
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Try connecting directly
docker-compose exec postgres psql -U swin -d vbac -c "SELECT 1"

# Restart PostgreSQL
docker-compose restart postgres
sleep 10
```

### Redis Connection Error

```bash
# Check Redis is running
docker-compose ps redis

# Check logs
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli ping

# Should return: PONG
```

### Kafka Issues

```bash
# Check Kafka is running
docker-compose ps kafka

# List topics
docker-compose exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --list

# Create test topic
docker-compose exec kafka kafka-topics.sh \
  --bootstrap-server kafka:9092 \
  --create \
  --topic test
```

### Celery Worker Not Processing Tasks

```bash
# Check worker status
docker-compose logs celery-worker

# Check active tasks
docker-compose exec celery-worker celery -A backend.tasks inspect active

# Restart worker
docker-compose restart celery-worker
```

### API Not Responding

```bash
# Check backend logs
docker-compose logs -f backend

# Check if container is running
docker-compose ps backend

# Restart backend
docker-compose restart backend

# Check API health
curl http://localhost:8080/docs
```

---

## 📊 Volume Management

### List Volumes

```bash
docker volume ls
```

### Inspect Volume

```bash
docker volume inspect vbac_postgres_data
docker volume inspect vbac_redis_data
```

### Backup Database

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U swin vbac > backup.sql

# Restore PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U swin -d vbac
```

### Clear Volumes

```bash
# Remove all volumes (clears all data)
docker-compose down -v

# Remove specific volume
docker volume rm vbac_postgres_data
```

---

## 🔄 Development Workflow

### 1. Start Development

```bash
bash docker-start.sh
bash docker-init-data.sh
```

### 2. Make Code Changes

Files in backend/ are auto-reloaded (mounted volume)

```bash
# Edit files locally
nano backend/main.py

# Changes apply immediately
```

### 3. View Changes

```bash
# Check logs
docker-compose logs -f backend

# Test API
curl http://localhost:8080/docs
```

### 4. Add New Dependencies

```bash
# Edit requirements.txt
nano requirements.txt

# Rebuild container
docker-compose build backend

# Restart service
docker-compose up -d backend
```

### 5. Stop Development

```bash
docker-compose stop

# Or completely remove
docker-compose down
```

---

## 🧪 Testing

### Test Database Connection

```bash
docker-compose exec backend python -c "
import asyncio
from app.core.db_instance import db_client

async def test():
    await db_client.connect()
    print('✓ Database connected')
    await db_client.close()

asyncio.run(test())
"
```

### Test Redis Connection

```bash
docker-compose exec redis redis-cli ping
# Output: PONG
```

### Test API

```bash
docker-compose exec backend python -c "
import requests
response = requests.get('http://localhost:8080/docs')
print(f'Status: {response.status_code}')
print('✓ API is responding')
"
```

### Test Celery

```bash
docker-compose exec celery-worker celery -A backend.tasks inspect active
```

---

## 📈 Performance Tips

### Increase Celery Concurrency

Edit docker-compose.yml:
```yaml
command: celery -A backend.tasks worker 
  --loglevel=info 
  -Q portfolio,recommend,realtime_price 
  --concurrency=8  # Increase from 4
```

Restart:
```bash
docker-compose restart celery-worker
```

### Use Production Database

For production, use managed PostgreSQL:
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    # ... your production credentials
```

### Enable Caching

Redis is already configured for caching. To increase:
```bash
docker-compose exec redis redis-cli
> CONFIG SET maxmemory 2gb
> CONFIG SET maxmemory-policy allkeys-lru
```

---

## 🔒 Security Considerations

⚠️ **WARNING**: This setup is for development only!

For production:
1. Change default PostgreSQL credentials
2. Use environment variables for secrets
3. Enable PostgreSQL SSL
4. Use Redis password protection
5. Implement Kafka security
6. Add API authentication
7. Use Docker secrets
8. Run as non-root user

---

## 📚 More Information

- See [QUICK_START.md](QUICK_START.md) for quick setup
- See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API reference
- See [DATA_SCRIPTS_GUIDE.md](DATA_SCRIPTS_GUIDE.md) for data scripts
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for manual setup

---

## 🎯 Next Steps

1. ✅ Run `bash docker-start.sh`
2. ✅ Run `bash docker-init-data.sh`
3. ✅ Access http://localhost:8080/docs
4. ✅ Test API endpoints
5. ✅ Deploy to production when ready

---

**Last Updated:** 2026-03-26
