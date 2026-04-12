from apscheduler.schedulers.background import BackgroundScheduler
from app.db import SessionLocal
from app import stock_service, crud


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