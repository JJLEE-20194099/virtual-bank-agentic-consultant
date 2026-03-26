# Virtual Bank Agentic Consultant - Complete Setup Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Data Simulation & Initialization](#data-simulation--initialization)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Overview
The Virtual Bank Agentic Consultant is an AI-powered virtual banking advisory system that integrates FastAPI, Celery, Kafka, PostgreSQL, and Redis to process stock trading data and provide intelligent investment advice.

### 1. Clone Repository

```bash
git clone https://github.com/JJLEE-20194099/virtual-bank-agentic-consultant.git
cd virtual-bank-agentic-consultant
```

### 2. Prepare Environment Variables (.env)

Copy the example environment file and configure it with your API keys:

```bash
cp .env.example .env
```

Open `.env` and fill in the required credentials. Below are detailed instructions for obtaining each API key:

#### **OpenAI API Key** (Required)
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**How to get it:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account (create one if you don't have it)
3. Click "Create new secret key"
4. Copy the generated key and paste it in your `.env` file
5. **Important**: Keep this key secure and never commit it to version control

#### **AWS Bedrock Setup** (Required for AI Agents)
```bash
AWS_ACCESS_KEY_ID=AKIA5XXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=wJalrXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=ap-southeast-1
BEDROCK_ROLE=arn:aws:iam::123456789012:role/BedrockAgentRole
```

**How to get AWS credentials:**
1. **Create AWS Account**: Go to [AWS Console](https://aws.amazon.com/console/) and create an account if you don't have one
2. **Navigate to IAM**: Go to [IAM Console](https://console.aws.amazon.com/iam/)
3. **Create User**:
   - Click "Users" → "Create user"
   - Enter username (e.g., "vbac-user")
   - Select "Provide user access to the AWS Management Console" if needed
   - Click "Next"
4. **Set Permissions**:
   - Click "Attach policies directly"
   - Search for and attach: `AmazonBedrockFullAccess`
   - You can also attach `AmazonS3FullAccess` if you plan to use S3
5. **Create Access Key**:
   - After user creation, go to "Security credentials" tab
   - Under "Access keys", click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Download the CSV file or copy the keys
6. **Copy Keys**:
   - `AWS_ACCESS_KEY_ID`: The Access Key ID from the CSV/download
   - `AWS_SECRET_ACCESS_KEY`: The Secret Access Key
7. **Choose Region**: Select a region where Bedrock is available (e.g., `us-east-1`, `us-west-2`, `ap-southeast-1`)

**Create Bedrock IAM Role:**
1. In IAM Console, click "Roles" → "Create role"
2. Choose "AWS service" → "Bedrock"
3. Attach the `AmazonBedrockFullAccess` policy
4. Name the role (e.g., "BedrockAgentRole")
5. Copy the Role ARN and paste it as `BEDROCK_ROLE`

#### **Hugging Face Token** (Required for ML Models)
```bash
HF_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**How to get it:**
1. Go to [Hugging Face](https://huggingface.co/settings/tokens)
2. Sign in to your Hugging Face account (create one if needed)
3. Click "New token"
4. Give it a name (e.g., "VBAC-Token")
5. Select "Read" permissions (usually sufficient)
6. Click "Generate token"
7. Copy the token (starts with `hf_`) and paste it in your `.env`

#### **VNSTOCK API Key** (Optional - Free tier available)
```bash
VNSTOCK_API_KEY=
```

**How to get it:**
- **Free Tier**: Leave empty - the system will work with free tier limitations
- **Premium**: Visit [VNSTOCK Documentation](https://docs.vnstock.site/) for premium access details

#### **EIA Oil API Key** (Optional)
```bash
OIL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**How to get it:**
1. Go to [EIA OpenData Registration](https://www.eia.gov/opendata/register/)
2. Fill out the registration form
3. Check your email for the API key
4. Copy and paste the key

### 3. Run Docker Startup Automation

```bash
./docker-startup-automation.sh
```

#### What this script does and how it works:

**Main Function**: The `docker-startup-automation.sh` script automates the entire Docker container startup and initialization process for the project.

**How it works**:
1. **Displays colored status messages** for easy monitoring
2. **Starts Docker Compose**: Runs `docker-compose up -d` to launch all services defined in `docker-compose.yml` in detached mode (background)
3. **Service Health Check**: Checks critical services (like Kafka) and restarts unhealthy ones
4. **Backend Readiness Wait**: Polls the backend API health endpoint (`/docs`) for up to 5 minutes until it's ready
5. **Optional Backend Restart**: Prompts user to optionally restart backend for a clean state
6. **Data Initialization**: Executes `docker-init-data.sh` to populate sample data
7. **Celery Worker Restart**: Restarts the Celery worker to ensure it's running properly

**Services Started**:
- **PostgreSQL** (main database, port 5432)
- **Redis** (cache and Celery broker, port 6379)
- **Kafka** and **Zookeeper** (message queue system)
- **Backend** (FastAPI server, port 8080)
- **Celery Worker** and **Celery Beat** (background task processing)
- **Adminer** (database management UI, port 8081)

**Note**: The script only starts containers and performs initial data setup. It doesn't handle additional steps like waiting for complete backend readiness or running separate data initialization. Verify service status with `docker-compose ps` or `docker-compose logs` before proceeding.

### 4. Data Initialization Process

The `docker-init-data.sh` script automatically runs these steps inside the backend container:

1. **Generate Synthetic Trading Data** (`gen_trading_data.py`)
2. **Correct Stock Prices** (`recorrect_stock_price.py`)
3. **Save Trading Data to Database** (`save_trading_data.py`)
4. **Update Latest Stock Prices** (`append_new_stock_price.py`)
5. **Calculate Portfolio Values** (`calculate_portfolio.py`)
6. **Generate User Accounts** (`gen_user_account.py`)
7. **Extract Trading Behavior Features** (`extract_trading_behaviour_features.py`)

### 5. Access the System

After successful startup:
- **API Documentation**: http://localhost:8080/docs
- **Database Admin UI**: http://localhost:8081
- **Redis**: localhost:6379

### 6. Next Steps

1. Check container status: `docker-compose ps`
2. Access API documentation to test endpoints
3. If additional sample data is needed, run individual Python scripts
4. Monitor logs: `docker-compose logs -f backend`


---

## Important Files & Directories

```
/
├── .env                           # Environment variables (create from .env.example)
├── .env.example                   # Example environment variables
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
✅ Access API documentation at http://localhost:8080/docs