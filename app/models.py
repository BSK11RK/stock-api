# テーブル定義
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db import Base


class StockPrice(Base):
    __tablename__ = "stock_price"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)