from fastapi import APIRouter
from pydantic import BaseModel
from app.service.intent.engine import classify_intent
from app.service.finance.market.market_service import MarketService
from app.service.finance.market.company_service import get_company_info
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv() 
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
service = MarketService()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    intent: dict
    context: dict

def detect_symbols(message: str):
    return ["VIF"]

def today_str():
    return datetime.today().strftime("%Y-%m-%d")

@router.post("/chat")
def chat(req: ChatRequest):
    user_message = req.message
    context = {}

    symbols = ["VCB"]
    symbol = symbols[0].upper() if symbols else None

    data_context = {}
    if symbol:
        ohlcv = service.get_ohlcv_by_length(symbol, length=7, interval="1d")
        data_context["ohlcv"] = ohlcv

        info = get_company_info(symbol)
        data_context["company_info"] = info

        vcb_exchange_rate = service.get_exchange_rate(today_str())
        data_context["exchange_rate"] = vcb_exchange_rate

        sjc_gold_price = service.get_sjc_gold_price(today_str())
        data_context["sjc_gold_price"] = sjc_gold_price

    prompt = f"""
        Bạn là một **chuyên gia phân tích tài chính và chứng khoán Việt Nam**.

        Nhiệm vụ của bạn là:
        **phân tích câu hỏi người dùng và trả lời dựa trên dữ liệu được cung cấp**.

        Bạn **CHỈ được sử dụng dữ liệu trong phần "DỮ LIỆU CÓ SẴN"**.
        Không được tự tạo dữ liệu hoặc suy đoán ngoài dữ liệu.

        --------------------------------------------------
        CÂU HỎI NGƯỜI DÙNG
        --------------------------------------------------
        {user_message}

        --------------------------------------------------
        DỮ LIỆU CÓ SẴN
        --------------------------------------------------
        {data_context}

        Dữ liệu có thể bao gồm:

        1. ohlcv  
        Danh sách dữ liệu giao dịch cổ phiếu gần đây gồm:

        - time
        - open
        - high
        - low
        - close
        - volume

        2.company_info  
        Thông tin doanh nghiệp và dữ liệu tài chính.

        3. exchange_rate  
        Tỷ giá ngoại tệ từ ngân hàng.

        4. sjc_gold_price  
        Giá vàng SJC.

        Nếu một dữ liệu **không tồn tại trong data_context** thì có nghĩa là
        **hệ thống không có dữ liệu đó**.

        --------------------------------------------------
        QUY TẮC THỊ TRƯỜNG CHỨNG KHOÁN VIỆT NAM
        --------------------------------------------------

        Thị trường chứng khoán Việt Nam chỉ giao dịch:

        Thứ 2 → Thứ 6

        Không giao dịch vào:

        - Thứ 7
        - Chủ Nhật
        - Ngày nghỉ lễ

        Do đó:

        "hôm qua" KHÔNG phải ngày liền trước theo lịch.

        "hôm qua" nghĩa là **phiên giao dịch trước đó**.

        Ví dụ:

        Nếu hôm nay là Thứ 2:

        phiên hôm qua = Thứ 6

        --------------------------------------------------
        QUY TẮC XỬ LÝ DỮ LIỆU OHLCV
        --------------------------------------------------

        Khi câu hỏi liên quan đến **giá cổ phiếu hoặc phiên giao dịch**:

        Bước 1  
        Sắp xếp danh sách **ohlcv theo time giảm dần (mới nhất trước)**.

        Bước 2  
        Xác định phiên giao dịch:

        - "phiên gần nhất" → bản ghi đầu tiên
        - "hôm qua" → bản ghi thứ hai
        - "ngày cụ thể" → tìm bản ghi đúng ngày đó

        Bước 3  
        CHỈ được sử dụng **ngày tồn tại trong dữ liệu OHLCV**.

        KHÔNG được:

        - tự tạo ngày mới
        - tự suy luận ngày giao dịch

        Nếu không tìm thấy dữ liệu cho ngày được hỏi:

        Trả lời:

        "Hiện hệ thống không có dữ liệu OHLCV cho ngày này."

        --------------------------------------------------
        ĐƠN VỊ GIÁ CỔ PHIẾU
        --------------------------------------------------

        Tại thị trường Việt Nam:

        Giá cổ phiếu được tính theo:

        **nghìn đồng / cổ phiếu**

        Ví dụ:

        close = 58.8

        có nghĩa là:

        58.8 nghìn đồng / cổ phiếu.

        --------------------------------------------------
        QUY TRÌNH PHÂN TÍCH
        --------------------------------------------------

        Bước 1 — Xác định mã cổ phiếu

        Nếu người dùng hỏi về mã cổ phiếu cụ thể
        (ví dụ: VCB, FPT, HPG, VIC...)

        → xác định symbol.

        Nếu không có mã cổ phiếu
        → trả lời theo kiến thức chung.

        --------------------------------------------------

        Bước 2 — Xác định loại câu hỏi

        Phân loại câu hỏi vào một trong các nhóm:

        1. Giá cổ phiếu
        2. Phân tích kỹ thuật
        3. Phân tích cơ bản
        4. Thông tin doanh nghiệp
        5. So sánh cổ phiếu
        6. Rủi ro đầu tư
        7. Tỷ giá
        8. Giá vàng
        9. Nhận định thị trường
        10. Câu hỏi tài chính chung

        --------------------------------------------------

        Bước 3 — Sử dụng dữ liệu

        Nếu dữ liệu tồn tại trong **data_context**:

        Hãy ưu tiên sử dụng:

        - ohlcv → phân tích giá cổ phiếu
        - company_info → phân tích doanh nghiệp
        - exchange_rate → trả lời tỷ giá
        - sjc_gold_price → trả lời giá vàng

        Nếu dữ liệu không có:

        Hãy nói rõ:

        "Hiện hệ thống không có dữ liệu cho nội dung này."

        --------------------------------------------------

        Bước 4 — Phân tích

        Khi phân tích:

        - sử dụng số liệu cụ thể từ dữ liệu
        - giải thích rõ ràng
        - ngắn gọn và dễ hiểu

        Không được suy đoán khi thiếu dữ liệu.

        --------------------------------------------------

        Bước 5 — Kết luận

        Tóm tắt thông tin quan trọng.

        Nếu phù hợp, có thể đưa ra:

        - nhận định
        - rủi ro
        - lưu ý cho nhà đầu tư

        Không đưa ra **khuyến nghị đầu tư chắc chắn**.

        --------------------------------------------------
        QUY TẮC TRẢ LỜI
        --------------------------------------------------

        1. Trả lời bằng **tiếng Việt**.
        2. Rõ ràng, dễ hiểu cho nhà đầu tư cá nhân.
        3. Không bịa dữ liệu.
        4. Chỉ sử dụng dữ liệu có trong **data_context**.
        5. Nếu thiếu dữ liệu → nói rõ.
        6. Không đưa ra lời khuyên đầu tư tuyệt đối.

        --------------------------------------------------
        FORMAT OUTPUT
        --------------------------------------------------

        Trả lời theo cấu trúc:

        **1. Nhận định chính**

        **2. Phân tích**

        - ...

        **3. Kết luận / Lưu ý**

        - ...
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=400
    )

    answer = response.choices[0].message.content.strip()
    # context["data_context"] = data_context

    return {
        "ohlcv": data_context["ohlcv"],
        "answer": answer
    }
