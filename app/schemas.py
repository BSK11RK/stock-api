from pydantic import BaseModel
from datetime import datetime
from typing import List

# ユーザー
class UserCreate(BaseModel):
    username: str
    password:str
    
    
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# 株
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