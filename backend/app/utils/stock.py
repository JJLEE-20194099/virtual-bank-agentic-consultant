def generate_question_set(portfolio_symbols):
    questions = []

    def pick(i):
        return portfolio_symbols[i % len(portfolio_symbols)]

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "price",
            "question": f"Giá hiện tại của {sym} là bao nhiêu?"
        })

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "analysis",
            "question": f"Phân tích xu hướng ngắn hạn của {sym}"
        })

    for i in range(0, len(portfolio_symbols) - 1, 2):
        s1 = portfolio_symbols[i]
        s2 = portfolio_symbols[i + 1]
        questions.append({
            "type": "compare",
            "question": f"So sánh {s1} và {s2} cổ phiếu nào tốt hơn?"
        })

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "impact",
            "question": f"Lãi suất hoặc USD ảnh hưởng thế nào tới {sym}?"
        })

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "company_info",
            "question": f"{sym} đang hoạt động trong lĩnh vực gì?"
        })

    questions.append({
        "type": "portfolio",
        "question": "Danh mục của tôi hiện tại đang thế nào?"
    })

    questions.append({
        "type": "portfolio",
        "question": "Tôi đang lỗ hay lãi bao nhiêu trong danh mục?"
    })

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "buy_sell",
            "question": f"Có nên giữ hay bán {sym} lúc này?"
        })

    questions.append({
        "type": "recommendation",
        "question": "Có cổ phiếu nào đáng mua trong thị trường hiện tại không?"
    })

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "risk",
            "question": f"{sym} có rủi ro cao không?"
        })

    questions.append({
        "type": "trend",
        "question": "Thị trường chứng khoán hôm nay thế nào?"
    })

    questions.append({
        "type": "trend",
        "question": "VNIndex đang trong xu hướng gì?"
    })

    for i in range(len(portfolio_symbols)):
        sym = pick(i)
        questions.append({
            "type": "volatility",
            "question": f"Cổ phiếu {sym} có biến động mạnh không?"
        })

    return questions
