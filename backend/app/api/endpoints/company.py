from fastapi import APIRouter, Query
from app.service.finance.market.company_service import get_company_info
import json
import os

router = APIRouter()



@router.get("/info/{company}")
def get_company_info_summary(
        company: str,
    ):    

    try:
        with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{company}/summary.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        pass

    with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/summary.json", "r", encoding="utf-8") as f:
        company_dict = json.load(f)
    
    
        
    data = get_company_info(company)

    os.makedirs(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{company}", exist_ok=True)

    with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{company}/financial.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    overview = data["overview"][0]
    outstanding_shares = overview["outstanding_shares"]
    listing_price = overview["listing_price"]
    

    def get_financial_value(category, section, item_id, year="2025"):
        records = data[category][section]
        for item in records:
            if item_id in item["item_id"]:
                try:
                    return item[year]
                except:
                    return item["2024"]
        return None


    profit_of_equity_holders = get_financial_value("income_statement", "yearly", "net_profit", "2025")
    profit_before_tax = get_financial_value("income_statement", "yearly", "profit_before_tax", "2025")
    profit_of_equity_holders = (profit_of_equity_holders / 1_000_000) if profit_of_equity_holders is not None else None
    profit_before_tax = (profit_before_tax / 1_000_000) if profit_before_tax is not None else None

    finance_idx = data.get("finance_idx", [])

    def get_index_value(item_id, year="2025"):
        for item in finance_idx:
            if  item_id in item["item_id"]:
                try:
                    return item[year]
                except:
                    return item["2024"]
        return None


    pe_ratio = get_index_value("p_e", "2025")
    dividend_yield_raw = get_index_value("dividend_yield", "2025")

    dividend_yield_percent = (dividend_yield_raw * 100) if dividend_yield_raw is not None else None

    if outstanding_shares and listing_price:
        market_cap_billion = (outstanding_shares * listing_price) / 1_000_000_000
    else:
        market_cap_billion = None

    company_info_summary = {
        "name": company_dict[company]["name"],
        "profit_of_equity_holders_billion_vnd": round(profit_of_equity_holders, 2) if profit_of_equity_holders else None,
        "profit_before_tax_billion_vnd": round(profit_before_tax, 2) if profit_before_tax else None,
        "pe_ratio": pe_ratio,
        "market_cap_billion_vnd": round(market_cap_billion, 2) if market_cap_billion else None,
        "dividend_yield_percent": round(dividend_yield_percent, 2) if dividend_yield_percent else None,
        "sector": company_dict[company]["sector"]
    }

    with open(f"/root/code/hackathon/virtual-bank-agentic-consultant/backend/app/data/company/{company}/summary.json", "w", encoding="utf-8") as f:
        json.dump(company_info_summary, f, ensure_ascii=False, indent=2)

    
    return company_info_summary



