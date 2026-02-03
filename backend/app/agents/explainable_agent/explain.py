from openai import OpenAI
from dotenv import load_dotenv      
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_explanation_signals(feature: dict, behaviors: list[str]) -> list[str]:
    signals = []

    if "big-spender" in behaviors:
        signals.append(
            f"Tổng chi tiêu trung bình hàng tháng của bạn ở mức tương đối cao "
            f"({int(feature['avg_monthly_spend']):,} VND)."
        )

    if "budget-conscious" in behaviors:
        signals.append(
            "Chi tiêu của bạn nhìn chung được kiểm soát ở mức hợp lý."
        )


    if "stable-spending" in behaviors:
        signals.append(
            "Mức chi tiêu của bạn khá ổn định giữa các tháng, "
            "cho thấy thói quen tài chính có tính kế hoạch."
        )

    if feature.get("spend_std", 0) > feature.get("avg_monthly_spend", 1) * 0.4:
        signals.append(
            "Chi tiêu của bạn có sự biến động đáng kể giữa các thời điểm."
        )


    if "travel-lover" in behaviors:
        travel_ratio = feature["category_ratio"].get("travel", 0)
        signals.append(
            f"Chi tiêu cho du lịch chiếm tỷ trọng đáng kể "
            f"(khoảng {int(travel_ratio*100)}% tổng chi tiêu gần đây)."
        )

    if "family-settled" in behaviors:
        signals.append(
            "Một phần lớn chi tiêu của bạn tập trung vào sinh hoạt gia đình "
            "như nhà ở và nhu yếu phẩm."
        )

    if "installment-dependent" in behaviors:
        signals.append(
            f"Bạn thường xuyên sử dụng hình thức trả góp "
            f"(khoảng {int(feature['installment_ratio']*100)}% số giao dịch)."
        )

    if "impulsive-spender" in behaviors:
        signals.append(
            "Một số khoản chi tiêu giá trị lớn xuất hiện trong thời gian ngắn, "
            "cho thấy xu hướng chi tiêu theo cảm xúc ở một vài thời điểm."
        )

    if "high-engagement-user" in behaviors:
        signals.append(
            f"Bạn sử dụng dịch vụ ngân hàng với tần suất cao "
            f"(trung bình {int(feature['frequency_monthly'])} giao dịch mỗi tháng)."
        )

    if feature.get("trend_3m") == "increasing":
        signals.append(
            "Tổng mức chi tiêu của bạn có xu hướng tăng dần trong vài tháng gần đây."
        )

    if feature.get("trend_3m") == "decreasing":
        signals.append(
            "Tổng mức chi tiêu của bạn có xu hướng giảm trong thời gian gần đây."
        )

    return signals

def explain(feature: dict, behaviors: list[str], products: list[str]) -> str:
    explanation_signals = build_explanation_signals(feature, behaviors)

    if not explanation_signals:
        explanation_signals = [
            "Hệ thống chưa ghi nhận điểm nổi bật rõ ràng trong thói quen chi tiêu gần đây của bạn."
        ]

    bullet_points = "\n".join([f"- {s}" for s in explanation_signals])

    products = ",".join(products)

    prompt = f"""
    Bạn là trợ lý tài chính của ngân hàng.

    Nhiệm vụ của bạn là GIẢI THÍCH LÝ DO hệ thống gợi ý sản phẩm tài chính cho người dùng,
    dựa trên dữ liệu hành vi chi tiêu đã quan sát được.

    Các nhận định – Thói quen giao dịch (đã được hệ thống xác định):
    {bullet_points}

    Sản phẩm được gợi ý:
    {products}

    Dữ liệu hành vi đã có:
    - Tổng chi tiêu 3 tháng gần nhất: {feature["total_spend_3m"]:,} VND
    - Chi tiêu trung bình mỗi tháng: {feature["avg_monthly_spend"]:,} VND
    - Mức dao động chi tiêu giữa các tháng: {feature["spend_std"]:,} VND
    - Xu hướng chi tiêu: {feature["trend_3m"]}
    - Danh mục chi tiêu chính: {feature["top_category"]}
    - Tỷ lệ chi tiêu theo danh mục: {feature["category_ratio"]}
    - Tần suất giao dịch trung bình mỗi tháng: {feature["frequency_monthly"]:.1f} giao dịch

    Yêu cầu OUTPUT:
    - Viết bằng tiếng Việt
    - KHÔNG viết theo dạng văn bản tự do
    - KHÔNG dùng từ ngữ mang tính cảm xúc hoặc marketing
    - Trình bày dưới dạng các gạch đầu dòng
    - Mỗi gạch đầu dòng phải:
    + Nêu 1 quan sát dữ liệu cụ thể
    + Giải thích mối liên hệ giữa quan sát đó và việc gợi ý sản phẩm
    - Chỉ mang tính giải thích, KHÔNG đưa ra lời khuyên hay kêu gọi sử dụng sản phẩm
    """


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý tài chính ngân hàng."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()
