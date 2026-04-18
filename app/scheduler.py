from apscheduler.schedulers.background import BackgroundScheduler
from app.db import SessionLocal
from app import stock_service, crud, models


# 定期取得する銘柄
TARGET_SYMBOLS = ["AAPL", "GOOGL", "AMZN", "TSLA", "7203.T", "6758.T", "7974.T"]


def fetch_and_store():
    db = SessionLocal()
    
    try:
        prices = stock_service.get_multiple_stock_prices(TARGET_SYMBOLS)
        
        for symbol, price in prices.items():
            crud.create_stock_price(db, symbol, price)
        print("Scheduled fetch completed")
    
    finally:
        db.close()
        
        
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store, "interval", minutes=60)
    scheduler.start()
    
    
def check_alerts():
    db = SessionLocal()
    alerts = db.query(models.Alert).all()
    
    for alert in alerts:
        price = stock_service.get_stock_price(alert.symbol)
        
        if price is None:
            continue
        
        if alert.condition == "above" and price >= alert.target_price:
            print(f"🔥 {alert.symbol} が {alert.target_price} 以上になりました！")

        elif alert.condition == "below" and price <= alert.target_price:
            print(f"🔥 {alert.symbol} が {alert.target_price} 以下になりました！")

    db.close()
    

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_alerts, "interval", minutes=1)
    scheduler.start()