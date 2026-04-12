from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, crud, stock_service
from app.db import SessionLocal, engine
from app.scheduler import start_scheduler


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# 起動時にスケジューラ開始
@app.on_event("startup")
def startup_event():
    start_scheduler()


# DBセッション
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# 単体取得＆保存
@app.post("/stocks/fetch", response_model=schemas.StockResponse)
def fetch_stock(symbol: str, db: Session = Depends(get_db)):
    price = stock_service.get_stock_price(symbol)
    
    if price is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return crud.create_stock_price(db, symbol, price)


# 複数取得
@app.post("/stocks/fetch-multiple", response_model=list[schemas.StockResponse])
def fetch_multiple_stocks(
    request: schemas.MultipleStockCreate,
    db: Session = Depends(get_db)
):
    results = stock_service.get_multiple_stock_prices(request.symbols)
    
    saved = []
    for symbol, price in results.items():
        if price is None:
            continue
        
        stock = crud.create_stock_price(db, symbol, price)
        saved.append(stock)
    return saved


# 履歴取得
@app.get("/stocks/{symbol}", response_model=list[schemas.StockResponse])
def read_stock(symbol: str, db: Session = Depends(get_db)):
    return crud.get_stock_prices(db, symbol)


# 1件取得
@app.get("/stock/{stock_id}", response_model=schemas.StockResponse)
def read_stock_by_id(stock_id: int, db: Session = Depends(get_db)):
    stock = crud.get_stock_by_id(db, stock_id)
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


# 削除
@app.delete("/stock/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = crud.delete_stock(db, stock_id)
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"message": "Deleted successfully"}