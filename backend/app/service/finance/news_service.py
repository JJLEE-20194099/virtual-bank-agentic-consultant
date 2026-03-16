def get_stock_info(symbols):

    info = {}

    for s in symbols:

        info[s] = {
            "sector": "Technology",
            "pe": 18.5
        }

    return info

