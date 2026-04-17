from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app import models, schemas, crud, stock_service, auth
from app.db import SessionLocal, engine
from app.scheduler import start_scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = crud.get_user(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ユーザー登録
@app.post("/auth/register", tags=["auth"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user.username, user.password)


# ログイン
@app.post("/auth/login", response_model=schemas.Token, tags=["auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, form_data.username)
    
    if not db_user or not auth.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


# 単体取得＆保存
@app.post("/stocks/fetch", response_model=schemas.StockResponse, tags=["stocks"])
def fetch_stock(
    symbol: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    price = stock_service.get_stock_price(symbol)
    
    if price is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return crud.create_stock_price(db, symbol, price, user.id)


# 認証追加
@app.post("/stocks/fetch-multiple", response_model=list[schemas.StockResponse], tags=["stocks"])
def fetch_multiple_stocks(
    request: schemas.MultipleStockCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user) 
):
    results = stock_service.get_multiple_stock_prices(request.symbols)
    
    saved = []
    for symbol, price in results.items():
        if price is None:
            continue
        
        stock = crud.create_stock_price(db, symbol, price, user.id)
        saved.append(stock)
    return saved


# 1件ずつシンボルで取得
@app.get("/stocks/{symbol}", response_model=list[schemas.StockResponse], tags=["stocks"])
def read_stock_by_symbol(
    symbol: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)  
):
    stocks = crud.get_stock_prices(db, symbol, user.id)
    result = []
    
    for s in stocks:
        company_name = stock_service.get_company_name(s.symbol)
        
        result.append({
            "id": s.id,
            "symbol": s.symbol,
            "company_name": stock_service.get_company_name(s.symbol),
            "price_usd": s.price,
            "price_jpy": stock_service.convert_to_jpy(s.price), 
            "timestamp": s.timestamp
        })
    return result


# 1件ずつIDで取得
@app.get("/stocks{stock_id}", response_model=schemas.StockResponse, tags=["stocks"])
def read_stock_by_id(
    stock_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)  
):
    stock = crud.get_stock_by_id(db, stock_id, user.id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return {
        "id": stock.id,
        "symbol": stock.symbol,
        "company_name": stock_service.get_company_name(stock.symbol),
        "price_usd": stock.price,
        "price_jpy": stock_service.convert_to_jpy(stock.price),
        "timestamp": stock.timestamp
    }


# 複数取得
@app.get("/stocks", response_model=list[schemas.StockResponse], tags=["stocks"])
def read_stocks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    stocks = crud.get_stocks(db, user.id, skip, limit)
    result = []
    
    for s in stocks:
        company_name = stock_service.get_company_name(s.symbol)
        price_jpy = stock_service.convert_to_jpy(s.price)
        
        result.append({
            "id": s.id,
            "symbol": s.symbol,
            "company_name": company_name,
            "price_usd": s.price,
            "price_jpy": price_jpy,
            "timestamp": s.timestamp
        })
    return result


# 削除
@app.delete("/stocks/{stock_id}", tags=["stocks"])
def delete_stock(
    stock_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user) 
):
    stock = crud.delete_stock(db, stock_id, user.id)
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return {"message": "Deleted successfully"}


# ウォッチリスト登録
@app.post("/watchlist", response_model=schemas.WatchListResponse,tags=["watchlist"])
def add_watchlist(
    item: schemas.WatchListCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    watch = crud.create_watchlist(db, item.symbol, user.id)
    price = stock_service.get_stock_price(watch.symbol)
    
    return {
        "id": watch.id,
        "symbol": watch.symbol,
        "company_name": stock_service.get_company_name(watch.symbol),
        "price_usd": price,
        "price_jpy": stock_service.convert_to_jpy(price)
    }


# ウォッチリスト一覧
@app.get("/watchlist", response_model=list[schemas.WatchListResponse], tags=["watchlist"])
def get_watchlist(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    watchlists = crud.get_watchlists(db, user.id)
    result = []
    
    for w in watchlists:
        price = stock_service.get_stock_price(w.symbol)
        company_name = stock_service.get_company_name(w.symbol)
        
        result.append({
            "id": w.id,
            "symbol": w.symbol,
            "company_name": stock_service.get_company_name(w.symbol),
            "price_usd": price,
            "price_jpy": stock_service.convert_to_jpy(price)
        })
    return result


# ウォッチリスト削除
@app.delete("/watchlist/{watch_id}", tags=["watchlist"])
def delete_watchlist(
    watch_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    watch = crud.delete_watchlist(db, watch_id, user.id)
    
    if not watch:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Deleted"}