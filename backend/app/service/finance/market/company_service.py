from vnstock import Company, Finance

from app.utils.clean import clean_financial_data
def get_company_info(company: str):
    comp = Company(symbol=company, source='KBS')
    finance = Finance(symbol=company, source='KBS')
    overview = comp.overview().to_dict(orient='records')

    balance_sheet = {
        "yearly": finance.balance_sheet(period='year').to_dict(orient='records'),
        "quarterly": finance.balance_sheet(period='quarter').to_dict(orient='records')
    }

    income_statement = {
        "yearly": finance.income_statement(period='year').to_dict(orient='records'),
        "quarterly": finance.income_statement(period='quarter').to_dict(orient='records')
    }

    cash_flow = {
        "yearly": finance.cash_flow(period='year').to_dict(orient='records'),
        "quarterly": finance.cash_flow(period='quarter').to_dict(orient='records')
    }

    finance_idx = finance.ratio(period='year', lang='vi').to_dict(orient='records')

    info = {
        "overview": overview,
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
        "cash_flow": cash_flow,
        "finance_idx": finance_idx
    }
    info = clean_financial_data(info)

    return info

