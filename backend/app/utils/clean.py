import math
def clean_financial_data(obj):
    if isinstance(obj, dict):
        return {k: clean_financial_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_financial_data(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj
    