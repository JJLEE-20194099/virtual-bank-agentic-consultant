# Virtual Bank Agentic Consultant - API Documentation

## Overview

The Virtual Bank Agentic Consultant (VBAC) is an AI-powered system that provides real-time assistance to bank advisors during customer conversations. It offers live transcription, conversation analysis, compliance checks, and financial product recommendations through a comprehensive RESTful API.

**Base URL:** `http://localhost:8080/api/v1`  
**API Version:** 1.0.0  
**Docs URL:** `http://localhost:8080/docs`

---

## Table of Contents

1. [Agent Management API](#agent-management-api)
2. [Conversation API](#conversation-api)
3. [Stock Transaction API](#stock-transaction-api)
4. [User Portfolio API](#user-portfolio-api)
5. [Transaction API](#transaction-api)
6. [Market Data API](#market-data-api)
7. [Company Information API](#company-information-api)

---

## Agent Management API

**Prefix:** `/agent`

Build and manage Bedrock agentic systems for AI-driven financial consulting.

### Create Agent

**Endpoint:** `POST /agent/create-agent`

Creates a new AI agent powered by AWS Bedrock.

**Request Body:**
```json
{
  "name": "string",
  "instruction": "string (agent system prompt)",
  "description": "string",
  "foundation_model": "string (e.g., apac.anthropic.claude-sonnet-4-20250514-v1:0)",
  "alias_name": "string"
}
```

**Response:**
```json
{
  "agent_id": "string",
  "status": "success"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/api/v1/agent/create-agent \
  -H "Content-Type: application/json" \
  -d '{
    "name": "portfolio-analyst",
    "instruction": "You are a stock portfolio analyst...",
    "description": "Analyzes stock portfolios",
    "foundation_model": "apac.anthropic.claude-sonnet-4-20250514-v1:0",
    "alias_name": "dev"
  }'
```

---

### Update Agent

**Endpoint:** `POST /agent/update-agent`

Updates an existing agent's configuration.

**Request Body:**
```json
{
  "agent_id": "string",
  "agent_name": "string",
  "instruction": "string",
  "description": "string",
  "foundation_model": "string"
}
```

**Response:**
```json
{
  "status": "success"
}
```

---

### Delete Agent

**Endpoint:** `POST /agent/delete-agent`

Deletes an agent and its aliases.

**Request Body:**
```json
{
  "agent_id": "string",
  "agent_alias_id": "string (optional, leave empty to delete all aliases)"
}
```

**Response:**
```json
{
  "status": "done" | "failed"
}
```

---

### Create Agent Alias

**Endpoint:** `POST /agent/create-alias`

Creates a new version/alias of an agent.

**Request Body:**
```json
{
  "agent_id": "string",
  "agent_alias_name": "string"
}
```

**Response:**
```json
{
  "agentAliasId": "string",
  "status": "success"
}
```

---

### Update Agent Alias

**Endpoint:** `POST /agent/update-alias`

Updates an agent alias configuration.

**Request Body:**
```json
{
  "agent_id": "string",
  "agent_alias_id": "string",
  "agent_alias_name": "string"
}
```

**Response:**
```json
{
  "status": "success"
}
```

---

### List All Agents

**Endpoint:** `GET /agent/list-agent`

Retrieves all available agents.

**Response:**
```json
{
  "agentSummaries": [
    {
      "agentId": "string",
      "agentName": "string",
      "agentStatus": "string",
      "latestAgentVersion": "string"
    }
  ]
}
```

---

### Get Agent Details

**Endpoint:** `GET /agent/{agent_id}`

Retrieves details and aliases of a specific agent.

**Path Parameters:**
- `agent_id` (string): The agent's unique identifier

**Response:**
```json
{
  "agentAliasSummaries": [
    {
      "agentAliasId": "string",
      "agentAliasName": "string",
      "agentAliasStatus": "string"
    }
  ]
}
```

---

## Conversation API

**Prefix:** `/conversation`

Handle real-time chat interactions with AI for market analysis and portfolio insights.

### Chat with OpenAI Assistant

**Endpoint:** `POST /conversation/chat`

Engage in conversation with the AI assistant for market analysis. Supports streaming responses.

**Request Body:**
```json
{
  "user_id": "string",
  "message": "string (user question or command)"
}
```

**Response:** Streaming response (text/plain)
```
{
  "analysis": "AI response with market insights",
  "intents": [...],
  "context": {...}
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/api/v1/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "C00001",
    "message": "Đánh giá rủi ro danh mục đầu tư của tôi"
  }'
```

---

### Chat with Bedrock Agent (Session-based)

**Endpoint:** `POST /conversation/bedrock-chat`

Advanced streaming chat using AWS Bedrock agent with session management.

**Request Body:**
```json
{
  "user_id": "string (default: C00001)",
  "message": "string (user query)",
  "session_id": "string (conversation session ID)",
  "agent_id": "string (Bedrock agent ID)",
  "agent_alias_id": "string (agent alias version ID)"
}
```

**Response:** Streaming response (text/plain)
```
{
  "response": "AI-generated response",
  "reasoning": "analysis process",
  "data": {...}
}
```

**Features:**
- Conversation history tracking
- Real-time market data context injection
- Portfolio-aware analysis
- Company information integration
- Real-time price data

---

### Test Chat (Offline)

**Endpoint:** `POST /conversation/test-chat`

Test agent response without streaming (useful for debugging).

**Request Body:**
```json
{
  "user_id": "string",
  "message": "string",
  "session_id": "string",
  "agent_id": "string",
  "agent_alias_id": "string"
}
```

**Response:**
```json
{
  "response": "test response",
  "output": "..."
}
```

---

## Stock Transaction API

**Prefix:** `/stock`

Manage stock buy/sell transactions and track portfolio positions.

### Get Stock Transactions (User & Symbol)

**Endpoint:** `GET /stock/{user_id}/{symbol}`

Retrieve all transactions for a user on a specific stock.

**Path Parameters:**
- `user_id` (string): Customer ID
- `symbol` (string): Stock ticker (e.g., FPT, VNM)

**Query Parameters:**
- `limit` (integer, default: 20): Number of results
- `offset` (integer, default: 0): Pagination offset

**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "string",
      "customer_id": "string",
      "stock_code": "string",
      "action": "buy" | "sell",
      "quantity": "number",
      "price": "number",
      "fee": "number",
      "datetime": "ISO8601"
    }
  ]
}
```

---

### Get All Stock Transactions (User)

**Endpoint:** `GET /stock/{user_id}`

Retrieve all stock transactions for a user across all stocks.

**Path Parameters:**
- `user_id` (string): Customer ID

**Query Parameters:**
- `limit` (integer, default: 20): Number of results
- `offset` (integer, default: 0): Pagination offset

**Response:**
```json
{
  "transactions": [
    {...}
  ],
  "total": "number"
}
```

---

### Buy/Sell Stock (Real-time)

**Endpoint:** `POST /stock/buy-sell`

Execute a buy or sell transaction at current market prices.

**Request Body:**
```json
{
  "customer_id": "string",
  "stock_code": "string",
  "action": "buy" | "sell",
  "quantity": "integer",
  "price": "number (-1 for current market price)"
}
```

**Response:**
```json
{
  "status": "ok",
  "transaction_id": "string"
}
```

**Behavior:**
- If `price = -1`, uses current market price from Redis cache
- Automatically calculates transaction fee (0.1% - 0.5%)
- Updates portfolio in background task
- Triggers product recommendation update

---

### Simulate Buy/Sell (Backtesting)

**Endpoint:** `POST /stock/buy-sell-simulation`

Execute a transaction at a past date for backtesting/simulation.

**Request Body:**
```json
{
  "customer_id": "string",
  "stock_code": "string",
  "action": "buy" | "sell",
  "quantity": "integer",
  "price": "number (-1 for market price at that time)",
  "datetime": "ISO8601 (past date)"
}
```

**Response:**
```json
{
  "status": "ok",
  "transaction_id": "string"
}
```

---

### Create Single Transaction

**Endpoint:** `POST /stock/transaction`

Create a single stock transaction record.

**Request Body:**
```json
{
  "transaction_id": "string",
  "customer_id": "string",
  "stock_code": "string",
  "action": "buy" | "sell",
  "quantity": "number",
  "price": "number",
  "fee": "number",
  "datetime": "ISO8601"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Bulk Create Transactions

**Endpoint:** `POST /stock/transaction/bulk`

Create multiple transactions at once.

**Request Body:**
```json
{
  "transactions": [
    {
      "transaction_id": "string",
      "customer_id": "string",
      "stock_code": "string",
      "action": "buy" | "sell",
      "quantity": "number",
      "price": "number",
      "fee": "number",
      "datetime": "ISO8601"
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "count": "number"
}
```

---

### Delete Transaction

**Endpoint:** `POST /stock/transaction/delete/{transaction_id}`

Delete a specific transaction.

**Path Parameters:**
- `transaction_id` (string): Transaction ID to delete

**Response:**
```json
{
  "status": "ok"
}
```

---

## User Portfolio API

**Prefix:** `/user`

Retrieve user portfolio details, behavior analysis, and product recommendations.

### Get Portfolio

**Endpoint:** `GET /user/portfolio/{user_id}`

Retrieve raw portfolio data for a user.

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "user_id": "string",
  "portfolio_stats": {
    "SYMBOL": {
      "quantity": "number",
      "average_cost": "number",
      "current_price": "number",
      "unrealized_pnl": "number",
      "pnl_percentage": "number"
    }
  },
  "total_portfolio_value": "number",
  "total_cost": "number"
}
```

---

### Get Portfolio Summary (Enriched)

**Endpoint:** `GET /user/summary/{user_id}`

Retrieve comprehensive portfolio summary with AI recommendations. **Cached for 60 seconds.**

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "market-news": {
    "date": "string",
    "trend": "bullish" | "bearish",
    "movement": "number",
    "data": {...}
  },
  "overall": {
    "total_portfolio_value": "number",
    "total_cost": "number",
    "cash_ratio": "number",
    "total_money": "number",
    "overall_risk": "number (1-10)",
    "available_cash": "number",
    "preferred_categories": ["string"],
    "risk_tolerance": "string"
  },
  "detail": {
    "SYMBOL": {
      "risk": "number (1-10)",
      "stock_summary": {...},
      "portfolio_summary": {...},
      "company_summary": {...}
    }
  },
  "recommend_data": [
    {
      "symbol": "string",
      "name": "string",
      "sector": "string",
      "pe": "number",
      "dividend": "number",
      "score": "number",
      "recommendation": "STRONG BUY" | "BUY" | "WATCHLIST" | "SKIP"
    }
  ]
}
```

---

### Get Stock Behavior Analysis

**Endpoint:** `GET /user/behaviour/{user_id}`

Get user's stock trading behavior and patterns.

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "user_id": "string",
  "trading_behavior": {
    "average_hold_days": "number",
    "win_rate": "number",
    "risk_profile": "conservative" | "moderate" | "aggressive",
    "preferred_sectors": ["string"]
  },
  "clustering_info": {...}
}
```

---

### Get Stock Product Recommendations

**Endpoint:** `GET /user/recommend/{user_id}`

Get AI-generated product recommendations. **Cached for 1 hour.**

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "recommendations": [
    {
      "symbol": "string",
      "recommendation": "string",
      "reason": "string",
      "risk_level": "low" | "medium" | "high",
      "confidence": "number"
    }
  ]
}
```

---

### Generate Product Recommendations (Async)

**Endpoint:** `POST /user/recommend/{user_id}`

Trigger async generation of product recommendations.

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "status": "queued",
  "task_id": "string"
}
```

**Note:** Uses Celery background task for asynchronous processing.

---

### Get Question Recommendations

**Endpoint:** `POST /user/question-list/{user_id}`

Get AI-generated questions for customer engagement.

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "questions": [
    {
      "question": "string",
      "category": "string",
      "difficulty": "easy" | "medium" | "hard"
    }
  ]
}
```

---

### Get Portfolio Advice

**Endpoint:** `GET /user/analyze/{user_id}`

Get comprehensive AI-generated portfolio advice. **Cached for 60 seconds.**

**Path Parameters:**
- `user_id` (string): Customer ID

**Response:**
```json
{
  "user_id": "string",
  "overall_assessment": "string",
  "risk_assessment": "string",
  "recommendations": [
    {
      "action": "buy" | "sell" | "hold",
      "symbol": "string",
      "reason": "string",
      "target_value": "number"
    }
  ]
}
```

---

## Transaction API

**Prefix:** `/transaction`

Track general financial transactions (not stock transactions).

### Get Transactions by Date Range

**Endpoint:** `GET /transaction/{user_id}`

Retrieve transactions for a user between specific dates.

**Path Parameters:**
- `user_id` (string): Customer ID

**Query Parameters:**
- `from` (string, required): Start date (YYYY-MM-DD)
- `to` (string, required): End date (YYYY-MM-DD)

**Response:**
```json
{
  "user_id": "string",
  "from": "string",
  "to": "string",
  "total_transactions": "number",
  "transactions": [
    {
      "user_id": "string",
      "type": "deposit" | "withdrawal" | "purchase" | "transfer",
      "amount": "number",
      "category": "string",
      "description": "string",
      "trx_time": "ISO8601",
      "installment": "object (optional)"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8080/api/v1/transaction/C00001?from=2025-12-30&to=2026-02-06"
```

---

### Trigger Transaction Event

**Endpoint:** `POST /transaction/trigger`

Record a new transaction and trigger AI analysis/recommendations.

**Request Body:**
```json
{
  "user_id": "string",
  "type": "string",
  "amount": "number",
  "category": "string (optional)",
  "description": "string (optional)",
  "trx_time": "ISO8601 (optional, defaults to now)"
}
```

**Response:**
```json
{
  "status": "ok",
  "user_id": "string",
  "transaction": {...},
  "result": {
    "consultation": "string",
    "recommendations": [...]
  }
}
```

**Behavior:**
- Creates transaction record
- Runs feature engineering job
- Invokes AI consultant for analysis
- Returns contextual recommendations

---

## Market Data API

**Prefix:** `/market`

Access real-time and historical market data for stocks, commodities, and forex.

### Get OHLCV Data by Date Range

**Endpoint:** `GET /market/ohlcv-by-date/{symbol}`

Retrieve OHLCV (Open, High, Low, Close, Volume) data between dates.

**Path Parameters:**
- `symbol` (string): Stock ticker (e.g., FPT, VNM, VNINDEX, GOLD, SILVER)

**Query Parameters:**
- `start_date` (string, required): Start date (YYYY-MM-DD)
- `end_date` (string, default: "-1"): End date or "-1" for today (YYYY-MM-DD)
- `interval` (string, default: "1d"): Time interval
  - Available: `1m`, `5m`, `15m`, `30m`, `1h`, `1H`, `60m`, `1d`, `1D`, `d`, `D`, `daily`, `1w`, `1W`, `w`, `W`, `weekly`, `1M`, `m`, `M`, `monthly`

**Response:**
```json
{
  "symbol": "string",
  "data": [
    {
      "timestamp": "ISO8601",
      "open": "number",
      "high": "number",
      "low": "number",
      "close": "number",
      "volume": "number"
    }
  ]
}
```

---

### Get OHLCV Data by Length

**Endpoint:** `GET /market/ohlcv-by-length/{symbol}`

Retrieve last N candles of OHLCV data.

**Path Parameters:**
- `symbol` (string): Stock ticker

**Query Parameters:**
- `length` (integer, default: 30): Number of data points
- `interval` (string, default: "1d"): Time interval

**Response:**
```json
{
  "symbol": "string",
  "data": [
    {
      "timestamp": "ISO8601",
      "open": "number",
      "high": "number",
      "low": "number",
      "close": "number",
      "volume": "number"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=30&interval=1d"
```

---

### Get Stock Summary

**Endpoint:** `GET /market/stock/summary/{userid}/{symbol}`

Retrieve comprehensive stock analysis including chart data, OHLCV analysis, and company info.

**Path Parameters:**
- `userid` (string): User ID
- `symbol` (string): Stock ticker

**Response:**
```json
{
  "symbol": "string",
  "trend": "bullish" | "bearish",
  "volatility": "number",
  "support_level": "number",
  "resistance_level": "number",
  "portfolio": {...},
  "company_info": {...},
  "risk_assessment": "number (1-10)",
  "ai_stock_analysis": "string",
  "investment_advice": "string",
  "chart_data": [...]
}
```

---

### Get Multiple Stock Prices

**Endpoint:** `POST /market/ohlcv-by-symbols`

Get current prices for multiple stocks.

**Request Body:**
```json
[
  "string (symbol)"
]
```

**Response:**
```json
[
  {
    "symbol": "string",
    "open_price": "number",
    "high_price": "number",
    "low_price": "number",
    "close_price": "number",
    "volume": "number",
    "timestamp": "ISO8601"
  }
]
```

---

### Get Exchange Rate

**Endpoint:** `GET /market/exchange-rate`

Get USD/VND and other major currency rates.

**Query Parameters:**
- `date` (string, required): Date (YYYY-MM-DD)

**Response:**
```json
{
  "date": "string",
  "rates": {
    "USD_VND": "number",
    "EUR_USD": "number",
    ...
  }
}
```

---

### Get Domestic Gold Price (Current)

**Endpoint:** `GET /market/domestic-gold-price`

Get current gold prices in Vietnam.

**Response:**
```json
{
  "date": "string",
  "bid": "number (VND/tael)",
  "ask": "number (VND/tael)"
}
```

---

### Get Domestic Gold Price (Historical)

**Endpoint:** `GET /market/domestic-gold-price-by-date`

Get historical domestic gold prices.

**Query Parameters:**
- `date` (string, required): Date (YYYY-MM-DD)

**Response:**
```json
{
  "date": "string",
  "bid": "number",
  "ask": "number"
}
```

---

### Get Global Gold Price

**Endpoint:** `GET /market/global-gold-price`

Get current global gold price in USD/oz.

**Response:**
```json
{
  "date": "string",
  "price": "number (USD/oz)"
}
```

---

### Get Global Oil Price

**Endpoint:** `GET /market/global-oil-price`

Get current WTI crude oil price.

**Response:**
```json
{
  "date": "string",
  "price": "number (USD/bbl)",
  "type": "WTI"
}
```

---

### Get Domestic Oil Price

**Endpoint:** `GET /market/domestic-oil-price`

Get current Vietnam domestic oil prices.

**Response:**
```json
{
  "date": "string",
  "e92": "number (VND/liter)",
  "e95": "number (VND/liter)",
  "diesel": "number (VND/liter)"
}
```

---

## Company Information API

**Prefix:** `/company`

Access comprehensive company financial information and analysis.

### Get Company Summary

**Endpoint:** `GET /company/info/{company}`

Retrieve company financial summary with key metrics.

**Path Parameters:**
- `company` (string): Company ticker (e.g., FPT, VNM)

**Response:**
```json
{
  "name": "string",
  "sector": "string",
  "profit_of_equity_holders_billion_vnd": "number",
  "profit_before_tax_billion_vnd": "number",
  "pe_ratio": "number",
  "market_cap_billion_vnd": "number",
  "dividend_yield_percent": "number"
}
```

**Behavior:**
- Returns cached data if available
- Fetches fresh data from CafeF API if not cached
- Calculates key financial metrics:
  - **PE Ratio**: Price-to-Earnings
  - **Market Cap**: Outstanding Shares × Listing Price
  - **Dividend Yield**: Annual Dividend / Current Price
- Stores summary data

**Example:**
```bash
curl http://localhost:8080/api/v1/company/info/FPT
```

**Response Example:**
```json
{
  "name": "FPT Telecom",
  "sector": "Information Technology",
  "profit_of_equity_holders_billion_vnd": 2500.45,
  "profit_before_tax_billion_vnd": 3100.50,
  "pe_ratio": 12.5,
  "market_cap_billion_vnd": 125000.00,
  "dividend_yield_percent": 4.25
}
```

---

## Authentication & Error Handling

### Authentication

Currently, the API does not enforce authentication. In production, you may want to add API key or JWT token validation.

### Error Responses

All error responses follow this format:

```json
{
  "detail": "Error description",
  "status_code": "number"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad Request (validation error)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error
- `503`: Service Unavailable

### Example Error Response

```json
{
  "detail": "Transactions data not found",
  "status_code": 500
}
```

---

## Rate Limiting & Caching

### Caching Strategy

The API uses Redis for caching to improve performance:

- **User Summary**: 60 seconds cache
- **User Recommendations**: 1 hour cache
- **Portfolio Analysis**: 60 seconds cache
- **Realtime Prices**: Updated continuously

Clear cache by deleting specific keys:
```bash
# Delete specific cache entry
redis-cli DEL "summary:C00001"

# Clear all user-related cache
redis-cli KEYS "summary:*" | xargs redis-cli DEL
```

---

## Background Tasks (Celery)

Certain operations are asynchronous using Celery:

### Available Background Tasks

1. **`update_portfolio`** - Recalculates portfolio after transaction
2. **`update_stock_product_recommendation`** - Generates new product recommendations

### Task Monitoring

Check Celery task status:
```bash
# Get task status
celery -A tasks inspect active

# View task queue
celery -A tasks inspect reserved
```

---

## System Architecture Overview

```
Frontend (WebSocket/HTTP)
    ↓
FastAPI Backend Gateway (/api/v1)
    ├── Agent Management (Bedrock)
    ├── Conversation Engine
    ├── Portfolio Management
    ├── Market Data Service
    └── Transaction Service
    ↓
External Services
    ├── AWS Bedrock (AI/ML)
    ├── Redis (Caching)
    ├── PostgreSQL (Database)
    ├── CafeF API (Company Data)
    └── Financial Data Providers
```

---

## Technology Stack

- **Framework**: FastAPI (Python)
- **Real-time Communication**: WebSocket
- **Message Queue**: Apache Kafka
- **AI/ML**: AWS Bedrock, OpenAI
- **Caching**: Redis
- **Database**: PostgreSQL
- **Task Queue**: Celery
- **Data Processing**: Pandas, NumPy

---

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:
```
OPENAI_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_key
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:password@localhost:5432/vbac
```

### 3. Start Server

```bash
# Development
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080

# Production
gunicorn backend.main:app -w 4 -b 0.0.0.0:8080
```

### 4. Access API Documentation

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

---

## Request Examples

### Get Portfolio Summary

```bash
curl -X GET http://localhost:8080/api/v1/user/summary/C00001
```

### Buy Stock

```bash
curl -X POST http://localhost:8080/api/v1/stock/buy-sell \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "C00001",
    "stock_code": "FPT",
    "action": "buy",
    "quantity": 100,
    "price": -1
  }'
```

### Chat with AI

```bash
curl -X POST http://localhost:8080/api/v1/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "C00001",
    "message": "What stocks should I buy now?"
  }'
```

### Get Market Data

```bash
curl "http://localhost:8080/api/v1/market/ohlcv-by-length/FPT?length=30&interval=1d"
```

### Get Company Info

```bash
curl http://localhost:8080/api/v1/company/info/FPT
```

---

## Support & Documentation

- **API Documentation**: http://localhost:8080/docs
- **GitHub Repository**: [Virtual Bank Agentic Consultant](https://github.com/JJLEE-20194099/virtual-bank-agentic-consultant)

---

**Last Updated:** 2026-03-26  
**API Version:** 1.0.0
