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
    
    
class StockResponse(BaseModel):
    id: int
    symbol: str
    company_name: str
    price: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
        
        
class MultipleStockCreate(BaseModel):
    symbols: List[str]
        

# ウォッチリスト
class WatchListCreate(BaseModel):
    symbol: str
    
    
class WatchListResponse(BaseModel):
    id: int 
    symbol: str
    company_name: str
    price: float | None
    
    class Config:
        from_attributes = True