# 🏦 Virtual Bank Agentic Consultant

An AI-powered virtual financial advisory system that processes trading data and delivers intelligent investment insights using modern data engineering and machine learning technologies.

---

## 🚀 Overview

**Virtual Bank Agentic Consultant (VBAC)** is a microservices-based platform designed to simulate a digital banking advisor. It integrates real-time data processing, AI agents, and financial analytics to support investment decision-making.

### 🔑 Key Features

* 📊 Synthetic stock trading data generation
* 🤖 AI-driven financial advisory agents
* ⚡ Real-time data processing with Kafka
* 🔄 Asynchronous task handling with Celery
* 🗄️ Scalable database architecture with PostgreSQL
* 🚀 RESTful APIs via FastAPI

---

## 🧱 Tech Stack

| Layer            | Technology          |
| ---------------- | ------------------- |
| Backend API      | FastAPI             |
| Task Queue       | Celery + Redis      |
| Messaging System | Kafka + Zookeeper   |
| Database         | PostgreSQL          |
| AI Integration   | OpenAI, AWS Bedrock |
| ML Models        | Hugging Face        |
| Containerization | Docker              |

---

## 📦 Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/JJLEE-20194099/virtual-bank-agentic-consultant.git
cd virtual-bank-agentic-consultant
```

---

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env` with your credentials:

```env
OPENAI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-southeast-1
BEDROCK_ROLE=
HF_KEY=
VNSTOCK_API_KEY=
OIL_API_KEY=
```

---

### 3. Start System with Docker

```bash
./docker-startup-automation.sh
```

This script will:

* Start all services via Docker Compose
* Wait for backend readiness
* Initialize sample data
* Restart workers if needed

---

## ⚙️ System Architecture

### Services

* **PostgreSQL** – Main database
* **Redis** – Cache & task broker
* **Kafka** – Event streaming
* **FastAPI Backend** – API layer
* **Celery Worker** – Background jobs
* **Adminer** – Database UI

---

## 🧪 Data Initialization

Automated via `docker-init-data.sh`:

* Generate synthetic trading data
* Normalize stock prices
* Store data into database
* Update latest prices
* Compute portfolio values
* Create user accounts
* Extract behavioral features

---

## 🌐 Access Points

| Service    | URL                        |
| ---------- | -------------------------- |
| API Docs   | http://localhost:8080/docs |
| Adminer UI | http://localhost:8081      |
| Redis      | localhost:6379             |

---

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py
│   ├── tasks.py
│   ├── celery_worker.py
│   └── app/
│       ├── api/
│       ├── agents/
│       ├── clients/
│       ├── core/
│       ├── service/
│       └── model/
│
├── scripts/
│   ├── gen_trading_data.py
│   ├── save_trading_data.py
│   ├── calculate_portfolio.py
│   └── gen_user_account.py
│
├── docker-compose.yml
├── docker-startup-automation.sh
├── docker-init-data.sh
└── .env.example
```

---

## 📊 Usage

### Check running services

```bash
docker-compose ps
```

### View logs

```bash
docker-compose logs -f backend
```

---

## 🛠️ Troubleshooting

| Issue                 | Solution                          |
| --------------------- | --------------------------------- |
| Services not starting | Ensure Docker is running          |
| API not accessible    | Check logs and port conflicts     |
| Missing data          | Re-run data initialization script |
| Worker not processing | Restart Celery container          |

```bash
docker-compose restart
```

---

## 🔮 Future Improvements

* Real-time trading integration
* Advanced portfolio optimization models
* User authentication & dashboards
* Frontend UI (React / Next.js)
* Deployment to cloud (AWS / GCP)

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 📄 License

This project is for educational and research purposes.

---

## 📬 Contact

For questions or collaboration, please reach out via GitHub Issues.

---

⭐ If you find this project useful, consider giving it a star!
