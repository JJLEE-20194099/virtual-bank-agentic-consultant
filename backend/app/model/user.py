from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal, List, Any


class StockUserBehaviourBase(BaseModel):
    
    customer_id: str 

    behaviour_data: Any