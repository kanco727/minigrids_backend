# app/db.py
import os
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # charge .env si présent

DB_USER = os.getenv("DB_USER", "minigrid")
DB_PASSWORD_RAW = os.getenv("DB_PASSWORD", "Marie1995")
DB_PASSWORD = quote_plus(DB_PASSWORD_RAW)  # encodage sécurisé
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "minigrid_db")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False, future=True
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
