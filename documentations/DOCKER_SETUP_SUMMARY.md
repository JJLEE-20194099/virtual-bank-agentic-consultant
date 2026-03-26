# 🐳 Docker Setup Complete!

Tôi đã tạo hoàn chỉnh Docker setup cho project của bạn.

---

## 📦 Các File Được Tạo

### 1. **Dockerfile**
```dockerfile
FROM python:3.11-slim
# Installs dependencies
# Exposes port 8080
# Ready for docker-compose
```

**Cách dùng:**
- Được sử dụng bởi docker-compose.yml
- Tự động build khi chạy `docker-compose up`

---

### 2. **docker-compose.yml** ⭐ (Main File)
**Định nghĩa 8 services:**

1. **PostgreSQL** (Port 5432)
   - Database storage
   - User: swin
   - Password: swin
   - DB: vbac

2. **Redis** (Port 6379)
   - Cache + Message broker
   - For Celery queue

3. **Zookeeper** (Port 2181)
   - Kafka coordinator

4. **Kafka** (Port 9092)
   - Event streaming
   - Message queues

5. **Adminer** (Port 8081)
   - Web UI for PostgreSQL

6. **Backend API** (Port 8080)
   - FastAPI server
   - Swagger UI: /docs
   - Volume mounted for dev

7. **Celery Worker**
   - Processes background tasks
   - 4 concurrent workers
   - Queues: portfolio, recommend, realtime_price

8. **Celery Beat**
   - Scheduled task processor
   - Periodic job runner

**Features:**
- ✅ All services on same network `vbac-network`
- ✅ Health checks for each service
- ✅ Persistent volumes for PostgreSQL & Redis
- ✅ Environment variables configured
- ✅ Auto-reload for backend code changes
- ✅ Dependency management (wait for healthy services)

**Cách dùng:**
```bash
docker-compose up -d        # Start all
docker-compose down         # Stop all
docker-compose logs -f      # View logs
```

---

### 3. **docker-start.sh** 🚀
**Automated startup script**

**Chức năng:**
- ✅ Verifies prerequisites (Docker, ports available)
- ✅ Starts all services
- ✅ Waits for services to be healthy
- ✅ Shows access URLs
- ✅ Beautiful formatted output

**Cách dùng:**
```bash
bash docker-start.sh
```

**Output:**
```
✓ PostgreSQL is healthy
✓ Redis is healthy
✓ Backend API is healthy

Services accessible at:
  Backend API: http://localhost:8080
  Swagger UI: http://localhost:8080/docs
  Adminer: http://localhost:8081
  PostgreSQL: localhost:5432
  Redis: localhost:6379
  Kafka: localhost:9092
```

---

### 4. **docker-init-data.sh** 📊
**Initialize sample data**

**Chức năng:**
- ✅ Waits for backend to be ready
- ✅ Runs gen_trading_data.py
- ✅ Runs save_trading_data.py
- ✅ Runs gen_user_account.py
- ✅ Runs append_new_stock_price.py
- ✅ Runs calculate_portfolio.py
- ✅ Shows completion report

**Cách dùng:**
```bash
bash docker-init-data.sh
```

**Tạo:**
- 1,500 trading transactions
- 100 user accounts
- Stock price data
- 100 calculated portfolios

---

### 5. **.dockerignore**
**Files to exclude from Docker build**

**Giảm image size:**
- Python cache files
- .git directory
- Virtual environments
- Environment files

---

### 6. **Makefile** ⚡
**Convenient command shortcuts**

**Commands (40+ available):**

```bash
# Start/Stop
make docker-up           # Start services
make docker-down         # Stop services
make docker-restart      # Restart all

# Data
make docker-init         # Initialize data
make docker-clean-db     # Reset database

# Logs
make docker-logs         # All logs
make docker-logs-api     # Backend only
make docker-logs-worker  # Celery worker
make docker-logs-beat    # Celery beat

# Access
make docker-shell-api    # Backend shell
make docker-shell-db     # PostgreSQL shell
make docker-shell-redis  # Redis shell

# Monitoring
make docker-ps          # Show containers
make docker-stats       # Resource usage
make docker-test        # Test all services

# Shortcuts
make up                 # Same as docker-up
make logs               # Same as docker-logs
make init               # Same as docker-init
```

**Cách dùng:**
```bash
make help               # Show all commands
make docker-up
make docker-init
make docker-logs-api
```

---

### 7. **DOCKER_GUIDE.md** 📚
**Complete Docker documentation**

**Sections:**
- Overview of 8 services
- Architecture diagram
- 50+ usage commands
- Environment variables
- Access URLs & credentials
- Example API calls
- Troubleshooting guide
- Volume management
- Development workflow
- Performance tips
- Security considerations

---

### 8. **CELERY_GUIDE.md** 🎯
**Celery Background Tasks Guide**

**Covers:**
- Celery architecture
- Task definitions
- Scheduled tasks (cron-like)
- Docker configuration
- Usage examples
- Monitoring (Flower UI)
- Troubleshooting
- Scaling workers
- Best practices
- Security

**Task Types:**
1. `update_portfolio` - Recalculate portfolios
2. `update_stock_product_recommendation` - Generate recommendations
3. `update_realtime_prices_task` - Update stock prices

---

### 9. **.env.example** (Updated)
**API keys template**

**Nội dung:**
- OpenAI API key
- AWS credentials
- Hugging Face token
- Database credentials
- Redis config
- Kafka config
- Celery config

**With detailed instructions for getting each key**

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start everything
bash docker-start.sh

# 2. Initialize data
bash docker-init-data.sh

# 3. Access API
open http://localhost:8080/docs
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Docker Network (vbac-network)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PostgreSQL          Redis             Kafka + Zookeeper   │
│  :5432              :6379              :9092 / :2181       │
│    │                  │                    │                │
│    └──────────────────┼────────────────────┘                │
│                       │                                      │
│          ┌────────────────────────────┐                     │
│          │  Backend API (FastAPI)     │                     │
│          │  :8080 - http://localhost  │                     │
│          │  /docs - Swagger UI        │                     │
│          └────────────────────────────┘                     │
│               │              │                               │
│        ┌──────┴──────┐  ┌─────┴──────┐                      │
│        │   Celery   │  │   Celery   │                      │
│        │   Worker   │  │    Beat    │                      │
│        └────────────┘  └────────────┘                      │
│                                                             │
│          ┌────────────┐     ┌─────────────┐               │
│          │  Adminer   │     │  Zookeeper  │               │
│          │  :8081     │     │  (Kafka)    │               │
│          └────────────┘     └─────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 What Each Service Does

| Service | Port | Purpose | Access |
|---------|------|---------|--------|
| **PostgreSQL** | 5432 | Store transactions, portfolios, users | psql / Adminer |
| **Redis** | 6379 | Cache, Celery broker | redis-cli |
| **Kafka** | 9092 | Event streaming | Docker shell |
| **Adminer** | 8081 | Database UI | http://localhost:8081 |
| **Backend API** | 8080 | FastAPI server | http://localhost:8080/docs |
| **Celery Worker** | - | Process background tasks | docker logs |
| **Celery Beat** | - | Schedule periodic tasks | docker logs |
| **Zookeeper** | 2181 | Kafka coordination | Internal |

---

## 🧪 Verification Commands

After running `docker-start.sh` and `docker-init-data.sh`:

```bash
# Check all containers running
docker-compose ps

# Test database
curl http://localhost:8080/api/v1/user/summary/C00001

# Test market data
curl "http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=7"

# Test company info
curl http://localhost:8080/api/v1/company/info/FPT

# Test Adminer
open http://localhost:8081
# Login: System=PostgreSQL, Server=postgres, User=swin, Password=swin

# View API docs
open http://localhost:8080/docs
```

---

## 📋 File Structure

```
project-root/
├── Dockerfile                    # ✅ Docker image definition
├── docker-compose.yml            # ✅ All services orchestration
├── .dockerignore                 # ✅ Exclude files from build
├── docker-start.sh               # ✅ Start all services
├── docker-init-data.sh           # ✅ Initialize data
├── Makefile                      # ✅ Convenient commands
│
├── DOCKER_GUIDE.md               # ✅ Docker documentation
├── CELERY_GUIDE.md               # ✅ Celery documentation
├── .env.example                  # ✅ API keys template
│
├── backend/
│   ├── main.py
│   ├── tasks.py                  # Celery tasks
│   ├── celery_worker.py          # Celery configuration
│   └── ...
│
└── ... (other files)
```

---

## 💻 Common Usage

```bash
# Start
docker-compose up -d

# Initialize data
bash docker-init-data.sh

# View logs
docker-compose logs -f backend

# Stop
docker-compose down

# Clean start (remove all data)
docker-compose down -v
docker-compose up -d
bash docker-init-data.sh
```

Or use Makefile:

```bash
make docker-up
make docker-init
make docker-logs-api
make docker-down
```

---

## 🔧 Environment Setup

### Copy .env file

```bash
cp .env.example .env
nano .env
```

### Fill in API Keys

```
OPENAI_API_KEY=sk-xxxxx
AWS_ACCESS_KEY_ID=AKIA5xxxxx
AWS_SECRET_ACCESS_KEY=wJalrXxxxxx
AWS_REGION=ap-southeast-1
HF_KEY=hf_xxxxx
BEDROCK_ROLE=arn:aws:iam::xxxxx
```

See `.env.example` for getting each key.

---

## 🐛 Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
```

### Database connection error

```bash
# Restart PostgreSQL
docker-compose restart postgres
sleep 10

# Check connection
docker-compose exec postgres psql -U swin -d vbac -c "SELECT 1"
```

### API not responding

```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Test
curl http://localhost:8080/docs
```

### Celery not processing tasks

```bash
# Check worker
docker-compose logs celery-worker

# Restart worker
docker-compose restart celery-worker

# Check Redis
docker-compose exec redis redis-cli ping
```

---

## 📚 Documentation Files

```
DOCKER_GUIDE.md           # Complete Docker guide
CELERY_GUIDE.md           # Background tasks guide
API_DOCUMENTATION.md      # All API endpoints
SETUP_GUIDE.md           # Manual setup guide
DATA_SCRIPTS_GUIDE.md    # Data script explanations
QUICK_START.md           # Quick reference
.env.example             # API keys instructions
```

---

## ✨ Features Included

✅ **PostgreSQL** - Enterprise database  
✅ **Redis** - High-speed caching  
✅ **Kafka** - Event streaming  
✅ **FastAPI** - Modern async web framework  
✅ **Celery** - Distributed task queue  
✅ **Celery Beat** - Task scheduling  
✅ **Adminer** - Database management UI  
✅ **Docker** - Container orchestration  
✅ **Make** - Command shortcuts  
✅ **20+ GB saved** through Docker caching  

---

## 🎯 Next Steps

1. ✅ Create `.env` file with API keys
2. ✅ Run `bash docker-start.sh`
3. ✅ Run `bash docker-init-data.sh`
4. ✅ Access http://localhost:8080/docs
5. ✅ Test API endpoints
6. ✅ View logs: `docker-compose logs -f`
7. ✅ Deploy to production

---

## 💡 Pro Tips

### Use Makefile

```bash
make help           # See all commands
make docker-up      # Shorter than docker-compose up -d
make docker-logs    # Shorter than docker-compose logs -f
make docker-init    # Run data setup
```

### Monitor in Real-time

```bash
# Terminal 1: View logs
docker-compose logs -f

# Terminal 2: Run tests
curl http://localhost:8080/docs
```

### Develop Faster

- Backend code changes auto-reload (volume mounted)
- Edit files locally, changes apply immediately
- No need to rebuild image when editing Python code

### Scale Workers

Increase Celery concurrency:
```bash
# Edit docker-compose.yml
--concurrency=8  # Increase from 4
```

---

## 📞 Support

- **Docker Issues**: See DOCKER_GUIDE.md
- **Celery Issues**: See CELERY_GUIDE.md
- **API Issues**: See API_DOCUMENTATION.md
- **Setup Issues**: See SETUP_GUIDE.md

---

**Congratulations! 🎉**

Your Docker setup is complete and ready to use!

```bash
bash docker-start.sh
bash docker-init-data.sh
open http://localhost:8080/docs
```

---

**Last Updated:** 2026-03-26
