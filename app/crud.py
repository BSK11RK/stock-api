# DB操作
from sqlalchemy.orm import Session
from app import models
from app.auth import hash_password


# ユーザー作成
def create_user(db: Session, username: str, password: str):
    user = models.User(
        username=username,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, username: str):
    return db.query(models.User) \
        .filter(models.User.username == username).first()


# 株価
def create_stock_price(db: Session, symbol: str, price: float):
    stock = models.StockPrice(symbol=symbol, price=price)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


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