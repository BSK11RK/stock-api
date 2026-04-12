# DB接続
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# .envから取得（なければデフォルト）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/stocks.db")

# dataフォルダ作成（SQLite用）
if DATABASE_URL.startswith("sqlite"):
    os.makedirs("data", exist_ok=True)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()