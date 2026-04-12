from pydantic import BaseModel
from datetime import datetime
from typing import List


class StockCreate(BaseModel):
    symbol: str
    
    
class MultipleStockCreate(BaseModel):
    symbols: List[str]
    
    
class StockResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    
    class Config:
        from_attributes = True