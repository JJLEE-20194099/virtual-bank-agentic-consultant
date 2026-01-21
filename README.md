# Virtual Bank Agentic Consultant

[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/JJLEE-20194099/virtual-bank-agentic-consultant/tree/prototype1)

The Virtual Bank Agentic Consultant (VBAC) is a real-time, AI-powered system designed to assist bank advisors during live conversations with customers. It provides live transcription, conversation analysis, compliance checks, and suggests relevant financial products, all in real-time.

This project leverages an event-driven architecture with Apache Kafka and a multi-agent system to process audio streams and generate actionable insights for bank agents.

## Features

*   **Real-time Speech-to-Text:** Low-latency transcription of conversations using OpenAI Whisper, streamed via gRPC for high performance.
*   **Agentic AI Engine:** A multi-agent system for intelligent data retrieval, financial consulting, and sales recommendations using Large Language Models.
*   **Event-Driven Architecture:** Utilizes Apache Kafka for a scalable and decoupled microservice pipeline that processes conversation events from transcription to recommendation.
*   **Comprehensive NLP Analysis:** Extracts intents, entities (NER), and sentiment from the conversation transcript to understand customer needs.
*   **Automated Compliance Monitoring:** Performs real-time checks to ensure the conversation adheres to financial regulations (e.g., MiFID II disclosure rules).
*   **Dynamic Recommendations:** Suggests relevant bank products and actions based on the live conversation, customer profile data, and identified intents.
*   **Web-based Interface:** A demonstration UI that captures microphone audio and displays the live transcript and AI-generated recommendations.

## System Architecture

The system processes audio and conversation data through a multi-stage, event-driven pipeline.

1.  **Audio Ingestion:**
    *   The **Frontend** captures audio from the user's microphone.
    *   Raw audio (PCM) is streamed over a **WebSocket** to the **FastAPI Backend Gateway**.

2.  **Speech-to-Text:**
    *   The gateway forwards the audio stream to a dedicated **gRPC STT Server**.
    *   The STT server uses the **OpenAI Whisper** model to transcribe the audio into text.
    *   The final transcript is published to the `conversation.transcript` Kafka topic.

3.  **Kafka Processing Pipeline:**
    *   **NLP Service:** Consumes from `conversation.transcript`, performs sentiment analysis, intent classification, and NER, then publishes the insights to the `conversation.nlp` topic.
    *   **Compliance Service:** Consumes from `conversation.nlp`, runs compliance checks against predefined rules, and publishes the enriched data to the `conversation.compliance` topic.
    *   **Recommendation Service:** Consumes from `conversation.compliance` and uses a `SaleAgent` to generate product recommendations. The final recommendations are published to the `conversation.recommendation` topic.

4.  **Displaying Results:**
    *   The **FastAPI Backend Gateway** consumes the final recommendations from Kafka.
    *   Results are sent to the **Frontend** via a separate WebSocket to be displayed to the user in real-time.

**Data Flow:**
```
[Frontend: Mic Audio] -> WebSocket -> [FastAPI Gateway] -> gRPC -> [STT Server (Whisper)]
                                                                           |
                                                                           v
                                                                   [Kafka: conversation.transcript]
                                                                           |
                                                                           v
                                                                   [NLP Service]
                                                                           |
                                                                           v
                                                                   [Kafka: conversation.nlp]
                                                                           |
                                                                           v
                                                                   [Compliance Service]
                                                                           |
                                                                           v
                                                                   [Kafka: conversation.compliance]
                                                                           |
                                                                           v
                                                                   [Recommendation Service]
                                                                           |
                                                                           v
                                                                   [Kafka: conversation.recommendation]
                                                                           |
                                                                           v
[Frontend: Display] <- WebSocket <- [FastAPI Gateway]
```

## Technologies Used

*   **Backend:** FastAPI, Python, Uvicorn
*   **AI/ML:** OpenAI Whisper, `transformers`, `spacy`
*   **Real-time Communication:** WebSockets, gRPC
*   **Messaging/Streaming:** Apache Kafka
*   **Frontend:** HTML, JavaScript (Web Audio API)
*   **Data:** JSON files for mock client, product, and intent data.

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   An Apache Kafka instance.

### 1. Clone the Repository

```bash
git clone https://github.com/jjlee-20194099/virtual-bank-agentic-consultant.git
cd virtual-bank-agentic-consultant
```

### 2. Set Up the Environment

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend/app/config/` directory and add your OpenAI API key:

```.env
OPENAI_API_KEY="your-openai-api-key"
```

### 3. Start Apache Kafka

If you have Kafka installed, you can use the provided script to start Zookeeper and the Kafka server.

```bash
# Make sure you are in the root directory where your Kafka installation lives
# (The script assumes a standard Kafka directory structure)
sh run.kf.sh
```

Ensure the following topics are created in Kafka (or that auto-creation is enabled): `conversation.transcript`, `conversation.nlp`, `conversation.compliance`, `conversation.recommendation`.

### 4. Run the Services

Open separate terminal windows for each of the following services.

1.  **STT gRPC Server:**
    ```bash
    python backend/stt_server.py
    ```

2.  **NLP Service (Kafka Consumer):**
    ```bash
    python backend/app/service/nlp/service.py
    ```

3.  **Compliance Service (Kafka Consumer):**
    ```bash
    python backend/app/service/compliance/service.py
    ```

4.  **Recommendation Service (Kafka Consumer):**
    ```bash
    python backend/app/service/recommendation/service.py
    ```

5.  **Main Backend Server (FastAPI):**
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```

### 5. Access the Application

Open your browser and navigate to `http://localhost:8000`.

You will be prompted for microphone access. Once granted, you can start speaking, and the application will display the live transcript and recommendations.
