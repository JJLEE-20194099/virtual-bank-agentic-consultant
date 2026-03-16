from fastapi import APIRouter, Query
from app.service.finance.market.company_service import get_company_info

router = APIRouter()

@router.get("/info/{company}")
async def get_ohlcv_by_date(
        company: str,
    ):    
    return get_company_info(company)



