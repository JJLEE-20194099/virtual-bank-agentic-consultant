from fastapi import FastAPI, WebSocket
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from app.config.endpoint import TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT
from app.service.gateway.grpc_client import STTClient
from app.service.stt import stt_pb2
from app.service.gateway.kafka_producer import publish_transcript

app = FastAPI()
stt_client = STTClient()

async def consume_from_kafka():
    consumer = AIOKafkaConsumer(
        "conversation.recommendation",
        bootstrap_servers=TRANSCRIPT_KAFKA_CONSUMER_ENDPOINT,
        group_id="recommendation-service"
    )
    
    await consumer.start()

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode('utf-8'))
            payload = data["payload"]
            recommendations = payload.get("recommendations")
            yield recommendations
    finally:
        await consumer.stop()


@app.websocket("/ws/text/{session_id}")
async def recommendation_ws(ws: WebSocket, session_id: str):
    await ws.accept()
    print(f"WS accepted session: {session_id}")
    async for recommendations in consume_from_kafka():
        await ws.send_json({
            "recommendations": recommendations
        })
    
    
    

@app.websocket("/ws/audio/{session_id}")
async def audio_ws(ws: WebSocket, session_id: str):
    await ws.accept()
    print(f"WS accepted session: {session_id}")

    audio_queue = asyncio.Queue()

    async def audio_gen():
        while True:
            chunk = await audio_queue.get()
            yield stt_pb2.AudioChunk(
                session_id=session_id,
                audio=chunk,
                sample_rate=16000
            )

    async def receive_audio():
        while True:
            data = await ws.receive_bytes()
            await audio_queue.put(data)

    async def send_transcript():
        async for transcript in stt_client.stream(audio_gen()):
            if transcript.text != "":
              publish_transcript(session_id, transcript)
              await ws.send_json({
                  "text": transcript.text,
                  "is_final": transcript.is_final,
                  "language": transcript.language
              })

    await asyncio.gather(
        receive_audio(),
        send_transcript()
    )


from fastapi.responses import HTMLResponse

@app.get("/")
async def get():
    return HTMLResponse("""
        <!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VBAC - Team</title>
  
  <style>
    body {
      font-family: Arial, sans-serif;
    }

    .customer-info {
      margin: 20px;
    }

    h2 {
      color: #2c3e50;
    }

    .section {
      margin-bottom: 20px;
    }

    .section h3 {
      color: #16a085;
    }

    .section p {
      font-size: 1.1em;
    }

    .loan-records, .credit-card-records {
      margin-top: 20px;
      border-top: 2px solid #2c3e50;
      padding-top: 10px;
    }

    .loan-records p, .credit-card-records p {
      font-size: 1em;
      margin-left: 20px;
    }
  </style>
</head>

<body>
  <h1>VBAC</h1>
  <div id="transcript-container">
    <h2>Transcript:</h2>
    <p id="transcript-text">Loading...</p>
    <h2>Recommendation:</h2>
    <p id="recommend-text">Loading...</p>
  </div>
  
  <h1>Thông Tin Khách Hàng</h1>
  
  <div id="customer-info" class="customer-info">
    <div class="section">
      <h3>Thông tin cá nhân</h3>
      <p id="customer-name"></p>
      <p id="customer-age"></p>
      <p id="customer-gender"></p>
      <p id="customer-marital-status"></p>
      <p id="customer-location"></p>
      <p id="customer-education"></p>
      <p id="customer-occupation"></p>
    </div>

    <div class="section">
      <h3>Thông tin thu nhập</h3>
      <p id="customer-monthly-income"></p>
      <p id="customer-income-type"></p>
      <p id="customer-employment-type"></p>
      <p id="customer-years-of-experience"></p>
    </div>

    <div class="section">
      <h3>Hành vi tài chính</h3>
      <p id="customer-spending-level"></p>
      <p id="customer-saving-habit"></p>
      <p id="customer-risk-appetite"></p>
    </div>

    <div class="loan-records">
      <h3>Khoản vay</h3>
      <div id="loan-records"></div>
    </div>

    <div class="credit-card-records">
      <h3>Thẻ tín dụng</h3>
      <div id="credit-card-records"></div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    const ws = new WebSocket("ws://localhost:8000/ws/audio/test123");

    ws.onopen = () => console.log("WS connected");
    ws.onerror = (err) => console.error("WS error", err);
    ws.onclose = (e) => console.log("WS closed", e);

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      console.log("Transcript:", msg.text, msg.is_final);
      const transcriptTextElement = document.getElementById("transcript-text");
      transcriptTextElement.textContent += " " + msg.text;

    };
    
    const text_ws = new WebSocket("ws://localhost:8000/ws/text/recommend_id");

    text_ws.onopen = () => console.log("Text WS connected");
    text_ws.onerror = (err) => console.error("Text WS error", err);
    text_ws.onclose = (e) => console.log("Text WS closed", e);

    text_ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      console.log(msg)
      console.log("Recommendations:", msg.recommendations);
      const recommendTextElement = document.getElementById("recommend-text");
      //recommendTextElement.textContent += " " + msg.recommendations;
      recommendTextElement.innerHTML = marked.parse(msg.recommendations); 

    };
    
    
    
    const customerData = {
    "customer_id": "VN_CUST_10",
    "personal_info": {
      "name": "Quý ông Trọng Đặng",
      "age": 56,
      "gender": "Male",
      "marital_status": "Married",
      "dependents": 2,
      "location": "Da Nang",
      "education_level": "High School",
      "occupation": "Doctor"
    },
    "income_profile": {
      "monthly_income_vnd": 54775910,
      "income_type": "Salary",
      "employment_type": "Full-time",
      "years_of_experience": 11
    },
    "financial_behavior": {
      "spending_level": "High",
      "saving_habit": "Regular",
      "risk_appetite": "High"
    },
    "credit_history": {
      "credit_score": 656,
      "total_active_loans": 3,
      "total_outstanding_debt_vnd": 349971357,
      "loan_records": [
        {
          "loan_id": "VN_LOAN_10_1",
          "loan_type": "Personal Loan",
          "bank": "Techcombank",
          "original_amount_vnd": 209357103,
          "outstanding_amount_vnd": 184388823,
          "interest_rate_percent": 14.8,
          "tenure_months": 240,
          "start_date": "2022-04-11",
          "repayment_status": "On-time",
          "late_payment_count": 0
        },
        {
          "loan_id": "VN_LOAN_10_2",
          "loan_type": "Auto Loan",
          "bank": "MB Bank",
          "original_amount_vnd": 653707597,
          "outstanding_amount_vnd": 94765958,
          "interest_rate_percent": 12.4,
          "tenure_months": 12,
          "start_date": "2025-08-12",
          "repayment_status": "On-time",
          "late_payment_count": 3
        },
        {
          "loan_id": "VN_LOAN_10_3",
          "loan_type": "Auto Loan",
          "bank": "VIB",
          "original_amount_vnd": 965927594,
          "outstanding_amount_vnd": 211362558,
          "interest_rate_percent": 8.3,
          "tenure_months": 12,
          "start_date": "2023-03-14",
          "repayment_status": "On-time",
          "late_payment_count": 0
        }
      ],
      "repaid_loans": [],
      "credit_card_records": [
        {
          "card_id": "VN_CARD_10_1",
          "card_type": "Credit Card",
          "bank": "Vietcombank",
          "credit_limit_vnd": 147339536,
          "annual_fee_vnd": 899138,
          "benefits": [
            "Air Miles",
            "Cashback"
          ],
          "monthly_spend_avg_vnd": 4261595,
          "usage_pattern": "Utilities & bills"
        }
      ]
    }
  };

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      const ctx = new AudioContext({ sampleRate: 16000 });
      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);

      source.connect(processor);
      processor.connect(ctx.destination);

      processor.onaudioprocess = e => {
        const pcm = e.inputBuffer.getChannelData(0);
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(float32ToPCM16(pcm));
        }
      };
    });

    function float32ToPCM16(float32) {
      const buffer = new ArrayBuffer(float32.length * 2);
      const view = new DataView(buffer);
      for (let i = 0; i < float32.length; i++) {
        let s = Math.max(-1, Math.min(1, float32[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      }
      return buffer;
    }
    
    

    // Function to load customer information
    function loadCustomerInfo(data) {
      document.getElementById('customer-name').textContent = `Name: ${data.personal_info.name}`;
      document.getElementById('customer-age').textContent = `Age: ${data.personal_info.age}`;
      document.getElementById('customer-gender').textContent = `Gender: ${data.personal_info.gender}`;
      document.getElementById('customer-marital-status').textContent = `Marital Status: ${data.personal_info.marital_status}`;
      document.getElementById('customer-location').textContent = `Location: ${data.personal_info.location}`;
      document.getElementById('customer-education').textContent = `Education: ${data.personal_info.education_level}`;
      document.getElementById('customer-occupation').textContent = `Occupation: ${data.personal_info.occupation}`;

      document.getElementById('customer-monthly-income').textContent = `Monthly Income: ${data.income_profile.monthly_income_vnd.toLocaleString()} VND`;
      document.getElementById('customer-income-type').textContent = `Income Type: ${data.income_profile.income_type}`;
      document.getElementById('customer-employment-type').textContent = `Employment Type: ${data.income_profile.employment_type}`;
      document.getElementById('customer-years-of-experience').textContent = `Years of Experience: ${data.income_profile.years_of_experience}`;

      document.getElementById('customer-spending-level').textContent = `Spending Level: ${data.financial_behavior.spending_level}`;
      document.getElementById('customer-saving-habit').textContent = `Saving Habit: ${data.financial_behavior.saving_habit}`;
      document.getElementById('customer-risk-appetite').textContent = `Risk Appetite: ${data.financial_behavior.risk_appetite}`;

      // Load loan records
      let loanRecordsHtml = '';
      data.credit_history.loan_records.forEach(loan => {
        loanRecordsHtml += `
          <p>Loan ID: ${loan.loan_id} - Type: ${loan.loan_type} - Bank: ${loan.bank} - Outstanding Amount: ${loan.outstanding_amount_vnd.toLocaleString()} VND</p>
        `;
      });
      document.getElementById('loan-records').innerHTML = loanRecordsHtml;

      // Load credit card records
      let creditCardRecordsHtml = '';
      data.credit_history.credit_card_records.forEach(card => {
        creditCardRecordsHtml += `
          <p>Card ID: ${card.card_id} - Type: ${card.card_type} - Bank: ${card.bank} - Credit Limit: ${card.credit_limit_vnd.toLocaleString()} VND</p>
        `;
      });
      document.getElementById('credit-card-records').innerHTML = creditCardRecordsHtml;
    }
    loadCustomerInfo(customerData);
  </script>
</body>

</html>
    """)