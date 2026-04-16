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
@app.post("/auth/login", tags=["auth"], response_model=schemas.Token)
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
@app.post("/stocks/fetch", tags=["stocks"], response_model=schemas.StockResponse)
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
@app.post("/stocks/fetch-multiple", tags=["stocks"], response_model=list[schemas.StockResponse])
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
@app.get("/stocks/{symbol}", tags=["stocks"], response_model=list[schemas.StockResponse])
def read_stock(
    symbol: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)  
):
    return crud.get_stock_prices(db, symbol, user.id)


# 1件ずつIDで取得
@app.get("/stock/{stock_id}", tags=["stocks"], response_model=schemas.StockResponse)
def read_stock_by_id(
    stock_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)  
):
    stock = crud.get_stock_by_id(db, stock_id, user.id)
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


# 複数取得
@app.get("/stocks", tags=["stocks"], response_model=list[schemas.StockResponse])
def read_stocks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    stocks = crud.get_stocks(db, user.id, skip, limit)
    return stocks


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
@app.post("/watchlist", tags=["watchlist"], response_model=schemas.WatchListResponse)
def add_watchlist(
    item: schemas.WatchListCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.create_watchlist(db, item.symbol, user.id)


# ウォッチリスト一覧
@app.get("/watchlist", tags=["watchlist"], response_model=list[schemas.WatchListResponse])
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
            "company_name": company_name,
            "price": price
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