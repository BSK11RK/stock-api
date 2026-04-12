# DB操作
from sqlalchemy.orm import Session
from app import models


# 作成
def create_stock_price(db: Session, symbol: str, price: float):
    db_stock = models.StockPrice(symbol=symbol, price=price)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


# 全件取得
def get_stock_prices(db: Session, symbol: str):
    return db.query(models.StockPrice) \
    .filter(models.StockPrice.symbol == symbol) \
    .order_by(models.StockPrice.timestamp.desc()).all()
    
    
# 1件取得
def get_stock_by_id(db: Session, stock_id: int):
    return db.query(models.StockPrice) \
        .filter(models.StockPrice.id == stock_id).first()
        
        
# 削除
def delete_stock(db: Session, stock_id: int):
    stock = db.query(models.StockPrice) \
        .filter(models.StockPrice.id == stock_id).first()
        
    if stock:
        db.delete(stock)
        db.commit()
    return stock