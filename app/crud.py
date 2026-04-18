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


# 株価作成
def create_stock_price(db: Session, symbol: str, price: float, user_id: int):
    stock = models.StockPrice(
        symbol=symbol, 
        price=price,
        user_id=user_id
    )
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock


# 全件取得
def get_stock_prices(db: Session, symbol: str, user_id: int):
    return db.query(models.StockPrice) \
    .filter(
        models.StockPrice.symbol == symbol,
        models.StockPrice.user_id == user_id
    ) \
    .order_by(models.StockPrice.timestamp.desc()).all()
    
    
# 1件取得
def get_stock_by_id(db: Session, stock_id: int, user_id: int):
    return db.query(models.StockPrice) \
        .filter(
            models.StockPrice.id == stock_id,
            models.StockPrice.user_id == user_id).first()
        
        
# 全件取得
def get_stocks(db: Session, user_id: int, skip: int, limit: int):
    return db.query(models.StockPrice) \
        .filter(models.StockPrice.user_id == user_id) \
        .order_by(models.StockPrice.timestamp.desc()) \
        .offset(skip).limit(limit).all()
        
        
# 削除
def delete_stock(db: Session, stock_id: int, user_id: int):
    stock = db.query(models.StockPrice) \
        .filter(
            models.StockPrice.id == stock_id,
            models.StockPrice.user_id == user_id).first()
        
    if stock:
        db.delete(stock)
        db.commit()
    return stock


# ウォッチリスト
def create_watchlist(db: Session, symbol: str, user_id: int):
    watch = models.WatchList(symbol=symbol, user_id=user_id)
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return watch


# 一覧取得
def get_watchlists(db: Session, user_id: int):
    return db.query(models.WatchList) \
        .filter(models.WatchList.user_id == user_id).all()
        
        
# 削除
def delete_watchlist(db: Session, watch_id: int, user_id: int):
    watch = db.query(models.WatchList) \
        .filter(models.WatchList.id == watch_id,
                models.WatchList.user_id == user_id).first()
        
    if watch:
        db.delete(watch)
        db.commit()
    return watch


# アラート作成
def create_alert(db: Session, data, user_id: int):
    alert = models.Alert(
        symbol=data.symbol,
        target_price=data.target_price,
        condition=data.condition,
        user_id=user_id
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# アラート一覧
def get_alerts(db: Session, user_id: int):
    return db.query(models.Alert) \
        .filter(models.Alert.user_id == user_id).all()
        
        
# アラート削除
def delete_alert(db: Session, alert_id: int, user_id: int):
    alert = db.query(models.Alert) \
        .filter(
            models.Alert.id == alert_id,
            models.Alert.user_id == user_id).first()
        
    if alert:
        db.delete(alert)
        db.commit()
    return alert