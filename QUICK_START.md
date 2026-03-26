# Quick Start Guide

Hướng dẫn bắt đầu nhanh nhất cho dự án Virtual Bank Agentic Consultant.

## 📋 Prerequisites (Yêu cầu)

- Docker & Docker Compose (hoặc cài PostgreSQL, Redis riêng)
- Python 3.8+
- Java 11+ (cho Kafka, nếu cần)
- Git

## Setup

### 1. Clone & Setup Python Environment

```bash
git clone https://github.com/JJLEE-20194099/virtual-bank-agentic-consultant.git
cd virtual-bank-agentic-consultant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Environment (.env file)

```bash
# Copy example to create .env
cp .env.example .env

# Edit .env file with your API keys (see SETUP_GUIDE.md for details)
nano .env
```

**Minimum required keys:**
```bash
OPENAI_API_KEY=sk-xxxxxx...
AWS_ACCESS_KEY_ID=AKIA5xxxxx...
AWS_SECRET_ACCESS_KEY=wJalrXxxxx...
AWS_REGION=ap-southeast-1
HF_KEY=hf_xxxxxx...
BEDROCK_ROLE=arn:aws:iam::xxxxx...
```

### 3. Start Infrastructure (Docker)

```bash
# Create network
docker network create swinnet

# PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_USER=swin \
  -e POSTGRES_PASSWORD=swin \
  -e POSTGRES_DB=vbac \
  -p 5432:5432 \
  --network swinnet \
  postgres:15-alpine

# Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  --network swinnet \
  redis:7-alpine

# Verify
docker ps | grep -E "postgres|redis"
```

### 4. Copy & Fix Trading Data

```bash
# The correct_trading_data.csv should exist
ls -lh correct_trading_data.csv

# If not, generate it
python gen_trading_data.py
```

### 5. Initialize Data (Run Scripts in Order)

**Terminal 1: Start Backend API**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080
# Wait until: "Uvicorn running on http://0.0.0.0:8080"
```

**Terminal 2: Run Setup Scripts**
```bash
# Make sure you're in project root
cd /root/code/hackathon/virtual-bank-agentic-consultant

# Step 1: Save trading data to database
python save_trading_data.py
# Expected: "Total: 1500" → "Status: 200 ✓"

# Step 2: Generate user accounts
python gen_user_account.py
# Expected: "✓ User C00001..." for 100 users

# Step 3: Update stock prices
python append_new_stock_price.py
# Expected: "FPT: ✓ Stored in Redis and JSON"

# Step 4: Calculate portfolio values
python calculate_portfolio.py
# Expected: "✓ Portfolio calculated for 100 users"
```

### 6. Verify Everything Works

```bash
# Check API
curl http://localhost:8080/docs

# Check sample data
curl http://localhost:8080/api/v1/user/summary/C00001

# Check stock data
curl http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=7

# Check company info
curl http://localhost:8080/api/v1/company/info/FPT
```

**Access Swagger UI (interactive docs):**
```
http://localhost:8080/docs
```

---

## 📁 File Structure After Setup

```
/root/code/hackathon/virtual-bank-agentic-consultant/
├── .env                          # Your API keys (create from .env.example)
├── API_DOCUMENTATION.md          # Complete API reference
├── SETUP_GUIDE.md               # Detailed setup instructions
├── DATA_SCRIPTS_GUIDE.md        # Detailed script explanations
├── QUICK_START.md               # This file
│
├── backend/
│   ├── main.py                  # FastAPI server
│   ├── tasks.py                 # Celery tasks (background jobs)
│   └── app/
│       ├── api/endpoints/       # API endpoints
│       ├── agents/              # AI agents
│       ├── data/                # Data files (auto-generated)
│       └── service/             # Business logic
│
├── correct_trading_data.csv     # Trading data (will be created)
└── synthetic_trading_data.csv   # Synthetic data (temp file)
```

---

## 📊 Data Population Flow

```
Step 1: gen_trading_data.py
        ↓
        Creates: synthetic_trading_data.csv
        
Step 2: save_trading_data.py
        ↓
        Uploads to DB: stock_transactions table
        (1500 transactions for 100 customers)
        
Step 3: gen_user_account.py
        ↓
        Creates users with cash allocation
        (100 user records)
        
Step 4: append_new_stock_price.py
        ↓
        Updates Redis cache + JSON files
        (FPT, VNM, TCB, ACB stock prices)
        
Step 5: calculate_portfolio.py
        ↓
        Computes portfolios (P&L, values)
        (100 portfolio records)
        
✓ System Ready!
```

---

## 🔑 Getting API Keys

### OpenAI API Key
1. Go: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy and paste into `.env`

### AWS Access Keys (for Bedrock)
1. Go: https://console.aws.amazon.com/iam/
2. Users → Your User → Security credentials
3. "Create access key"
4. Copy `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### Hugging Face Token
1. Go: https://huggingface.co/settings/tokens
2. New token → Type: "read"
3. Copy token

### AWS Bedrock Role
1. Go: https://console.aws.amazon.com/iam/home#/roles
2. Create role with Bedrock permissions
3. Copy ARN

**See SETUP_GUIDE.md for detailed steps per service**

---

## 🧪 Test API Endpoints

### Get User Portfolio
```bash
curl http://localhost:8080/api/v1/user/summary/C00001
```

### Buy Stock
```bash
curl -X POST http://localhost:8080/api/v1/stock/buy-sell \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C00001",
    "stock_code": "FPT",
    "action": "buy",
    "quantity": 10,
    "price": -1
  }'
```

### Chat with AI
```bash
curl -X POST http://localhost:8080/api/v1/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "C00001",
    "message": "Danh mục của tôi thế nào?"
  }'
```

### Get Market Data
```bash
curl "http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=30&interval=1d"
```

See **API_DOCUMENTATION.md** for all endpoints.

---

## 🚨 Troubleshooting

### Backend not starting?
```bash
# Check port 8080 is free
lsof -i :8080

# Check database connection
python -c "from backend.app.core.db_instance import db_client; print('DB OK')"
```

### Database connection error?
```bash
# Check PostgreSQL
docker ps | grep postgres

# Restart if needed
docker restart postgres
sleep 5
```

### Redis error?
```bash
# Check Redis
redis-cli ping
# Should return: PONG

# Restart if needed
docker restart redis
```

### Scripts failing?
```bash
# Make sure backend is running
# Make sure PostgreSQL and Redis are running
# Check .env file has all required keys
cat .env | grep -E "OPENAI|AWS|HF"
```

---

## 📚 Documentation

| File | Content |
|------|---------|
| **API_DOCUMENTATION.md** | Complete API reference with examples |
| **SETUP_GUIDE.md** | Detailed setup with infrastructure setup |
| **DATA_SCRIPTS_GUIDE.md** | Deep dive into each data script |
| **QUICK_START.md** | This file - quick reference |
| **.env.example** | Environment variable template with instructions |

---

## 🎯 Next Steps

### After Setup
1. ✅ Explore Swagger UI: http://localhost:8080/docs
2. ✅ Try some API calls with test data
3. ✅ Add custom trading data if needed
4. ✅ Deploy to production

### Advanced Features
- Start Celery worker for background tasks
- Setup Kafka for streaming
- Configure email notifications
- Add custom AI agent instructions

---

## 📞 Common Commands

```bash
# Start everything
docker start postgres redis
cd backend && uvicorn main:app --host 0.0.0.0 --port 8080

# View logs
docker logs -f postgres
docker logs -f redis

# Access database
psql -U swin -d vbac -h localhost

# Check API health
curl http://localhost:8080/api/v1/user/portfolio/C00001

# View Swagger UI
open http://localhost:8080/docs  # macOS
xdg-open http://localhost:8080/docs  # Linux
```

---

## ✨ What's Included

- ✅ Real-time market data API
- ✅ Stock portfolio management
- ✅ AI-powered recommendations (Bedrock agents)
- ✅ User transaction tracking
- ✅ P&L calculations
- ✅ Risk analysis
- ✅ RESTful API with Swagger docs
- ✅ Caching layer (Redis)
- ✅ Background task queue (Celery)
- ✅ Comprehensive test data

---

## 💡 Tips

- Use **Swagger UI** to test APIs visually
- Check **logs** in terminal when errors occur
- Use **redis-cli** to debug cache issues
- Use **psql** to query raw database
- Keep **.env** file for sensitive keys (don't commit)

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-26

For detailed information, see:
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [DATA_SCRIPTS_GUIDE.md](DATA_SCRIPTS_GUIDE.md)
