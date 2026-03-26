# Virtual Bank Agentic Consultant - Complete Setup Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Data Simulation & Initialization](#data-simulation--initialization)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+) or macOS
- **Python**: 3.8+
- **Docker**: 20.10+ (or install services separately)
- **Java**: 11+ (for Kafka)
- **Git**: For cloning the repository

### Required Services

- PostgreSQL 12+
- Redis 6+
- Apache Kafka 3.8+
- Celery (Python task queue)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/JJLEE-20194099/virtual-bank-agentic-consultant.git
cd virtual-bank-agentic-consultant
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` file and configure:

#### **OpenAI API Key**

```bash
# 1. Go to https://platform.openai.com/api-keys
# 2. Click "Create new secret key"
# 3. Copy the key and paste in .env:
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### **AWS Bedrock Setup**

```bash
# 1. Go to https://console.aws.amazon.com/
# 2. Open IAM Console → Users
# 3. Select your IAM user → Security credentials
# 4. "Create access key" and copy:
AWS_ACCESS_KEY_ID=AKIA5XXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=wJalrXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=ap-southeast-1  # Choose appropriate region

# 5. Create IAM Role for Bedrock:
#    - Go to https://console.aws.amazon.com/iam/home#/roles
#    - Create role with Bedrock permissions
#    - Copy ARN and paste:
BEDROCK_ROLE=arn:aws:iam::123456789012:role/BedrockAgentRole
```

#### **Hugging Face Token** (for ML models)

```bash
# 1. Go to https://huggingface.co/settings/tokens
# 2. Click "New token" (type: read)
# 3. Copy token:
HF_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### **Vietnam Stock API**

```bash
# VNSTOCK API is free tier only (no key needed)
# But if you have premium access:
VNSTOCK_API_KEY=your_key_here
```

#### **Oil Prices API**

```bash
# 1. Go to https://www.eia.gov/opendata/register/
# 2. Register and get API key
OIL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Infrastructure Setup

### Option 1: Using Docker (Recommended)

#### Setup PostgreSQL, Redis, and Adminer

```bash
# Create Docker network
docker network create swinnet

# Run PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_USER=swin \
  -e POSTGRES_PASSWORD=swin \
  -e POSTGRES_DB=vbac \
  -p 5432:5432 \
  --network swinnet \
  postgres:15-alpine

# Run Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  --network swinnet \
  redis:7-alpine

# Run Adminer (optional, for DB management UI)
docker run -d \
  --name adminer \
  -p 8081:8080 \
  --network swinnet \
  adminer:latest

# Verify containers are running
docker ps | grep -E "postgres|redis|adminer"
```

**Access UI:**
- PostgreSQL: `localhost:5432` (use psql or Adminer)
- Adminer Web UI: `http://localhost:8081`
  - System: PostgreSQL
  - Server: postgres
  - Username: swin
  - Password: swin
  - Database: vbac

### Option 2: Manual Installation

#### Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Create database
sudo -u postgres createdb vbac
sudo -u postgres psql -c "CREATE USER swin WITH PASSWORD 'swin';"
sudo -u postgres psql -c "ALTER ROLE swin WITH CREATEDB;"
```

#### Install Redis

```bash
# Ubuntu/Debian
sudo apt-get install -y redis-server

# Start Redis
redis-server

# Test connection
redis-cli ping  # Should return PONG
```

#### Install Apache Kafka

```bash
# Install Java
sudo apt-get install -y openjdk-11-jdk

# Download and extract Kafka
cd /opt
sudo wget https://downloads.apache.org/kafka/3.8.0/kafka_2.12-3.8.0.tgz
sudo tar -xzf kafka_2.12-3.8.0.tgz
sudo mv kafka_2.12-3.8.0 kafka
sudo chown -R $USER:$USER kafka

# Add to PATH
echo 'export PATH=$PATH:/opt/kafka/bin' >> ~/.bashrc
source ~/.bashrc

# Format Kafka storage (KRaft mode)
kafka-storage.sh format \
  -t abcd-1234 \
  -c /opt/kafka/config/kraft/server.properties

# Start Kafka server
kafka-server-start.sh /opt/kafka/config/kraft/server.properties

# Create topics (in another terminal)
kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic conversation.transcript \
  --partitions 3 \
  --replication-factor 1

kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic conversation.nlp \
  --partitions 3 \
  --replication-factor 1

kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic conversation.compliance \
  --partitions 3 \
  --replication-factor 1

kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic conversation.recommendation \
  --partitions 3 \
  --replication-factor 1

# List all topics
kafka-topics.sh --bootstrap-server localhost:9092 --list
```

---

## Data Simulation & Initialization

### Step 1: Initialize Database Tables

The database tables are automatically created when the backend starts. However, you can manually init them:

```bash
cd backend
python -c "
import asyncio
from app.core.db_instance import db_client

async def init():
    await db_client.connect()
    await db_client.init_portfolio_table()
    await db_client.init_stock_transactions_table()
    await db_client.init_portfolio_advice_table()
    await db_client.init_stock_user_behaviour_table()
    await db_client.init_user_table()
    await db_client.init_stock_product_recommendation_table()
    print('✓ All tables initialized')
    await db_client.close()

asyncio.run(init())
"
```

### Step 2: Generate Synthetic Trading Data

```bash
cd /root/code/hackathon/virtual-bank-agentic-consultant

# Generate synthetic trading data CSV
python gen_trading_data.py

# This creates: synthetic_trading_data.csv
# Check the file was created:
head synthetic_trading_data.csv
```

**Output:**
```csv
transaction_id,customer_id,stock_code,datetime,action,quantity,price,fee
C00001_FPT_2025-01-15T10:30:00,C00001,FPT,2025-01-15 10:30:00,buy,100,50.5,150.5
C00001_VNM_2025-01-16T14:15:00,C00001,VNM,2025-01-16 14:15:00,buy,50,100.0,250.0
...
```

### Step 3: Save Trading Data to Database

This script uploads the synthetic trading data to PostgreSQL:

```bash
# Run from project root directory
python save_trading_data.py
```

**What it does:**
- Reads `correct_trading_data.csv` (synthetic data)
- Batches transactions in chunks of 200
- POSTs to API: `POST /api/v1/stock/transaction/bulk`
- Saves all transactions to database

**Expected output:**
```
Total: 1500
200 transactions uploaded...
400 transactions uploaded...
600 transactions uploaded...
...
✓ All transactions saved successfully
```

### Step 4: Generate User Accounts

```bash
# Creates user accounts in the database
python gen_user_account.py
```

**What it does:**
- Fetches all unique customer IDs from transactions table
- Analyzes portfolio status for each user:
  - If large losses detected → higher cash reserves (16-25%)
  - If bullish stocks → lower cash reserves (1-4%)
  - If large portfolio → medium cash reserves (8-15%)
  - Otherwise → high cash reserves (40-60%)
- Inserts user records with `available_cash`

**Expected output:**
```
✓ User C00001 initialized with 15000.50 VND cash
✓ User C00002 initialized with 25000.00 VND cash
✓ User C00003 initialized with 5000.25 VND cash
...
```

### Step 5: Append New Stock Prices (Update Market Data)

This script fetches latest stock prices and updates the database:

```bash
# Fetch and update stock prices
python append_new_stock_price.py
```

**What it does:**
- Loads existing stock price history from cache
- Gets latest date from existing data
- Fetches missing data from market API (vnstock)
- Calculates technical indicators:
  - **Trend**: Bullish/Bearish (using SMA 20 vs SMA 50)
  - **Price Change**: Daily percentage change
  - **Support/Resistance**: High/Low levels
- Stores updated prices in Redis cache
- Updates JSON files: `/app/data/stock/{SYMBOL}/history_price.json`

**Expected output:**
```
Updating FPT price history...
  Latest date: 2025-03-24
  Fetching from 2025-03-25...
  ✓ 2 new candles added
  Trend: bullish | Change: +2.5%

Updating VNM price history...
  Latest date: 2025-03-24
  ✓ 1 new candle added
  Trend: bearish | Change: -1.2%
```

### Step 6: Calculate/Update Portfolio Values

```bash
# Calculate portfolio values for all users
python calculate_portfolio.py
```

**What it does:**
1. Fetches all customer transaction history
2. For each user:
   - Calculates holdings per stock (quantity, average cost)
   - Gets current market prices from Redis cache
   - Computes PnL (profit/loss):
     - `Unrealized PnL = (current_price - average_cost) × quantity`
     - `PnL % = (current_price - average_cost) / average_cost × 100%`
   - Computes portfolio metrics:
     - Total portfolio value
     - Total invested cost
     - Cash ratio
     - Overall risk score
3. Saves portfolio to database via API

**Expected output:**
```
Calculating portfolio for C00001...
  Total invested: 500,000 VND
  Current value: 525,000 VND
  Unrealized PnL: +25,000 VND (+5.0%)
  ✓ Portfolio saved

Calculating portfolio for C00002...
  Total invested: 1,200,000 VND
  Current value: 1,180,000 VND
  Unrealized PnL: -20,000 VND (-1.67%)
  ✓ Portfolio saved
```

### Step 7: Fetch Company Information

Optional: Fetch and cache company financial data:

```bash
# Fetch company info for specific stock
python -c "
from backend.app.service.finance.market.company_service import get_company_info
import json

symbols = ['FPT', 'VNM', 'TCB', 'ACB']

for symbol in symbols:
    data = get_company_info(symbol)
    print(f'✓ {symbol} - PE: {data.get(\"pe_ratio\")}, Market Cap: {data.get(\"market_cap_billion_vnd\")}B VND')
"
```

### Full Simulation Sequence

Run all steps in order:

```bash
#!/bin/bash
# Run from project root

echo "Step 1: Generate synthetic trading data..."
python gen_trading_data.py

echo "Step 2: Save trading data to database..."
python save_trading_data.py

echo "Step 3: Generate user accounts..."
python gen_user_account.py

echo "Step 4: Update stock prices..."
python append_new_stock_price.py

echo "Step 5: Calculate portfolio values..."
python calculate_portfolio.py

echo "✓ Data simulation complete!"
```

Or run all at once:

```bash
python gen_trading_data.py && \
python save_trading_data.py && \
python gen_user_account.py && \
python append_new_stock_price.py && \
python calculate_portfolio.py && \
echo "✓ Complete!"
```

---

## Running the Application

### 1. Start Backend API Server

```bash
cd backend

# Development mode (with auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Production mode
gunicorn main:app -w 4 -b 0.0.0.0:8080 -k uvicorn.workers.UvicornWorker
```

**Access:**
- Swagger Docs: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- API: http://localhost:8080/api/v1

### 2. Start Celery Worker (Background Tasks)

Open a new terminal:

```bash
cd backend

# Start Celery worker
celery -A tasks worker --loglevel=info

# Or use the provided script:
bash start_celery_worker.sh
```

### 3. Start Celery Beat (Scheduled Tasks)

Open another terminal:

```bash
cd backend

# Start Celery Beat scheduler
celery -A tasks beat --loglevel=info

# Or use the provided script:
bash start_celery_beat.sh
```

### 4. Start STT (Speech-to-Text) Server (Optional)

For audio transcription:

```bash
cd backend

python stt_server.py
```

---

## Verify Installation

### Check Database Connection

```bash
# Using psql
psql -U swin -d vbac -h localhost -c "SELECT version();"

# Or using Python:
python -c "
import asyncio
from app.core.db_instance import db_client

async def check():
    await db_client.connect()
    print('✓ Database connected')
    await db_client.close()

asyncio.run(check())
"
```

### Check Redis Connection

```bash
redis-cli ping
# Expected output: PONG
```

### Check API Health

```bash
curl http://localhost:8080/docs
# Should return Swagger UI HTML
```

### Query Sample Data

```bash
# Get user portfolio
curl http://localhost:8080/api/v1/user/portfolio/C00001

# Get market data
curl "http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=7"

# Get company info
curl http://localhost:8080/api/v1/company/info/FPT
```

---

## Important Files & Directories

```
/
├── .env                           # Environment variables (create from .env.example)
├── .env.example                   # Example environment variables
├── requirements.txt               # Python dependencies
├── setup.sh                       # Infrastructure setup script
├── gen_trading_data.py            # Generate synthetic trading data
├── save_trading_data.py           # Save data to database
├── gen_user_account.py            # Create user accounts
├── append_new_stock_price.py      # Update stock prices
├── calculate_portfolio.py         # Calculate portfolio values
│
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── tasks.py                   # Celery background tasks
│   ├── celery_worker.py           # Celery worker configuration
│   ├── stt_server.py              # Speech-to-text gRPC server
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/         # API route handlers
│   │   ├── agents/                # AI agent implementations
│   │   ├── clients/               # Database & API clients
│   │   ├── core/                  # Core configurations
│   │   ├── data/                  # Static data files
│   │   ├── service/               # Business logic services
│   │   └── model/                 # Database models
│   │
│   └── app/data/
│       ├── company/               # Company financial data
│       ├── stock/                 # Stock price histories
│       └── portfolio/             # Portfolio summaries
│
└── notebooks/                     # Jupyter notebooks for analysis
```

---

## Next Steps

1. ✅ Follow this guide to setup all infrastructure
2. ✅ Run data simulation scripts
3. ✅ Start backend server
4. ✅ Access API documentation at http://localhost:8080/docs
5. ✅ Test endpoints using Swagger UI
6. ✅ Deploy to production when ready

---

