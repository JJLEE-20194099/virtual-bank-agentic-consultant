# Celery Configuration Guide

Complete guide to Celery setup for background tasks and scheduling.

## 📝 Overview

Celery is a distributed task queue that processes background jobs asynchronously.

**Components:**
- **Celery Worker** - Executes tasks
- **Celery Beat** - Schedules periodic tasks
- **Redis** - Message broker (queue storage)
- **Backend** - Result backend (task results storage)

---

## 🏗️ Architecture

```
┌─────────────┐
│   Task      │  (e.g., update_portfolio())
│  Definition │
└──────┬──────┘
       │
       ├─→ [Queue via Redis]
       │
       ├─→ [Celery Worker] → Executes task
       │
       └─→ [Result Backend] → Stores result
```

---

## 📋 Docker Configuration

### Celery Worker Service

```yaml
celery-worker:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: vbac-celery-worker
  command: celery -A backend.tasks worker 
    --loglevel=info 
    -Q portfolio,recommend,realtime_price 
    --concurrency=4
  environment:
    CELERY_BROKER_URL: redis://redis:6379/0
    CELERY_RESULT_BACKEND: redis://redis:6379/1
  depends_on:
    - redis
    - postgres
  restart: unless-stopped
```

**Explanation:**
- `celery -A backend.tasks worker` → Start worker using tasks.py
- `--loglevel=info` → Log level (debug, info, warning, error)
- `-Q portfolio,recommend,realtime_price` → Named queues to process
- `--concurrency=4` → Number of parallel workers

### Celery Beat Service

```yaml
celery-beat:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: vbac-celery-beat
  command: celery -A backend.tasks beat --loglevel=info
  environment:
    CELERY_BROKER_URL: redis://redis:6379/0
    CELERY_RESULT_BACKEND: redis://redis:6379/1
  depends_on:
    - redis
    - postgres
  restart: unless-stopped
```

**Explanation:**
- Runs scheduled tasks at specified intervals
- Reads configuration from `backend/tasks.py`
- Sends tasks to worker queue

---

## 🎯 Task Definitions

Located in: `backend/tasks.py`

### Available Tasks

#### 1. Update Portfolio

```python
@app.task(bind=True, queue='portfolio')
def update_portfolio(self, customer_id: str):
    """
    Recalculate portfolio after transaction
    
    Triggered when: Buy/Sell transaction occurs
    Queue: portfolio
    """
    # Calculate new P&L, holdings, risk score
    pass
```

#### 2. Update Stock Recommendations

```python
@app.task(bind=True, queue='recommend')
def update_stock_product_recommendation(self, transaction: dict):
    """
    Generate new product recommendations
    
    Triggered when: User makes transaction
    Queue: recommend
    """
    # Analyze portfolio, market trends
    # Generate relevant product recommendations
    pass
```

#### 3. Update Realtime Prices

```python
@celery_app.task(bind=True, queue='realtime_price')
def update_realtime_prices_task():
    """
    Update stock prices in Redis
    
    Scheduled: Every 5 minutes
    Queue: realtime_price
    """
    # Fetch latest prices from market API
    # Store in Redis cache
    pass
```

---

## ⏰ Scheduled Tasks (Celery Beat)

Define periodic tasks in `backend/tasks.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-prices-every-5min': {
        'task': 'backend.tasks.update_realtime_prices_task',
        'schedule': 300.0,  # Every 5 minutes (seconds)
    },
    'update-portfolios-daily': {
        'task': 'backend.tasks.calculate_all_portfolios',
        'schedule': crontab(hour=21, minute=0),  # 21:00 every day
    },
    'clean-cache-hourly': {
        'task': 'backend.tasks.cleanup_expired_cache',
        'schedule': 3600.0,  # Every hour
    },
}
```

**Schedule Types:**
- `300.0` → Every 300 seconds (5 minutes)
- `3600.0` → Every 3600 seconds (1 hour)
- `86400.0` → Every 86400 seconds (1 day)
- `crontab(hour=21, minute=0)` → Specific time (21:00)

---

## 🚀 Usage Examples

### Trigger Task from API

```python
from backend.tasks import update_portfolio

# Async execution (returns immediately)
task = update_portfolio.delay(customer_id="C00001")

# Get task ID
print(task.id)

# Check task status
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE
```

### Trigger Task with Signature

```python
from backend.tasks import update_portfolio

# For retrying, chaining, or scheduling
sig = update_portfolio.s(customer_id="C00001")

# Apply with countdown (execute after 60 seconds)
sig.apply_async(countdown=60)

# Or immediately
result = sig.apply_async()
```

### Chain Multiple Tasks

```python
from celery import chain

# Execute sequentially
workflow = chain(
    update_portfolio.s("C00001"),
    update_stock_product_recommendation.s(),
    notify_user.s("C00001")
)

# Start workflow
result = workflow.apply_async()
```

---

## 📊 Monitoring Celery

### Docker Commands

```bash
# View Celery worker status
docker-compose exec celery-worker celery -A backend.tasks inspect active

# View registered tasks
docker-compose exec celery-worker celery -A backend.tasks inspect registered

# View worker statistics
docker-compose exec celery-worker celery -A backend.tasks inspect stats

# View queues
docker-compose exec celery-worker celery -A backend.tasks inspect active_queues

# View scheduled tasks (Beat)
docker-compose logs celery-beat | grep "Scheduler"
```

### Celery Flower (Web UI)

Optional: Add Flower for visual monitoring

```bash
# Install
pip install flower

# Start (runs on port 5555)
celery -A backend.tasks flower

# Access
open http://localhost:5555
```

Or add to docker-compose.yml:

```yaml
flower:
  image: python:3.11-slim
  command: pip install flower && flower -A backend.tasks --port=5555
  ports:
    - "5555:5555"
  depends_on:
    - celery-worker
```

---

## 🔍 Troubleshooting

### Worker Not Receiving Tasks

```bash
# Check worker is running
docker-compose ps celery-worker

# Check logs
docker-compose logs celery-worker

# Check queue
docker-compose exec redis redis-cli
> KEYS "*"  # Should see task queue

# Restart worker
docker-compose restart celery-worker
```

### Tasks Stuck in Queue

```bash
# View pending tasks
docker-compose exec celery-worker celery -A backend.tasks inspect reserved

# Clear queue
docker-compose exec redis redis-cli FLUSHDB

# Restart worker
docker-compose restart celery-worker
```

### Beat Not Scheduling Tasks

```bash
# Check beat is running
docker-compose logs celery-beat

# Look for "Scheduler" messages
docker-compose logs celery-beat | grep Scheduler

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart beat
docker-compose restart celery-beat
```

### Task Timeout

Increase task timeout in docker-compose.yml:

```yaml
command: celery -A backend.tasks worker 
  --task-time-limit=1800  # Timeout after 30 minutes
  --task-soft-time-limit=1500  # Soft timeout after 25 minutes
```

---

## 📈 Scaling

### Increase Worker Concurrency

**For I/O-bound tasks (API calls, DB queries):**

```yaml
command: celery -A backend.tasks worker 
  --concurrency=16  # More workers for I/O
  -P prefork  # Prefork mode (default)
```

**For CPU-bound tasks:**

```yaml
# Use gevent
pip install gevent

command: celery -A backend.tasks worker 
  --concurrency=4 
  -P gevent
```

### Use Multiple Worker Nodes

Add more workers for specific queues:

```yaml
celery-worker-portfolio:
  # ... (same as regular worker)
  -Q portfolio  # Only portfolio queue

celery-worker-recommend:
  # ... (same as regular worker)
  -Q recommend  # Only recommend queue

celery-worker-realtime:
  # ... (same as regular worker)
  -Q realtime_price  # Only realtime queue
```

---

## 🎯 Best Practices

### 1. Use Named Queues

```python
# Specify queue for each task
@app.task(queue='portfolio')
def update_portfolio(customer_id):
    pass

@app.task(queue='recommend')
def get_recommendations(customer_id):
    pass

# Start separate workers for each queue
# celery -A tasks worker -Q portfolio
# celery -A tasks worker -Q recommend
```

### 2. Handle Failures

```python
@app.task(bind=True, max_retries=3)
def risky_task(self):
    try:
        # Do something risky
        pass
    except Exception as exc:
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)
```

### 3. Set Timeouts

```python
@app.task(time_limit=300, soft_time_limit=250)
def long_running_task():
    # Timeout after 5 minutes
    # Soft signal after 4.17 minutes
    pass
```

### 4. Log Properly

```python
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task
def my_task():
    logger.info("Starting task")
    logger.error("Error occurred")
    logger.debug("Debug info")
```

### 5. Use Task Signatures

```python
# Delay execution
update_portfolio.apply_async(
    args=("C00001",),
    countdown=60  # Wait 60 seconds
)

# Schedule at specific time
from datetime import datetime, timedelta
eta = datetime.utcnow() + timedelta(hours=1)
update_portfolio.apply_async(
    args=("C00001",),
    eta=eta
)
```

---

## 🔐 Security

### Use Message Signing

```python
app.conf.security_key_file = '/path/to/key'
app.conf.security_certificate_file = '/path/to/cert'
app.conf.security_cert_store = '/path/to/ca-certs'
```

### Restrict Task Execution

```python
# Only certain users can execute tasks
@app.task
def admin_only_task():
    if not current_user.is_admin:
        raise PermissionError("Admin only")
```

---

## 📚 Files & Locations

```
backend/
├── tasks.py              # Task definitions
├── celery_worker.py      # Celery app configuration
├── start_celery_worker.sh  # Start worker script
└── start_celery_beat.sh    # Start beat script

docker-compose.yml       # Celery services
CELERY_GUIDE.md         # This file
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View worker status
docker-compose exec celery-worker celery -A backend.tasks inspect active

# View scheduled tasks
docker-compose logs celery-beat

# Restart worker
docker-compose restart celery-worker

# Restart beat
docker-compose restart celery-beat

# View logs
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

---

## 🎯 Common Tasks

### Get Task Status

```python
from backend.celery_worker import celery_app

task_id = "abc123"
task = celery_app.AsyncResult(task_id)

print(task.status)     # PENDING, STARTED, SUCCESS, FAILURE
print(task.result)     # Task result
print(task.traceback)  # If failed
```

### Cancel Task

```python
from backend.celery_worker import celery_app

task_id = "abc123"
celery_app.control.revoke(task_id, terminate=True)
```

### Retry Failed Task

```python
from backend.celery_worker import celery_app

task_id = "abc123"
celery_app.control.revoke(task_id)  # Cancel
update_portfolio.delay("C00001")      # Retry
```

---

## 📖 Documentation

- [Celery Official Docs](https://docs.celeryproject.io/)
- [Celery Best Practices](https://docs.celeryproject.io/en/latest/internals/protocol.html)
- [Celery Signals](https://docs.celeryproject.io/en/latest/userguide/signals.html)

---

**Last Updated:** 2026-03-26
