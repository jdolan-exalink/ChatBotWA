import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Usar SQLite por defecto en data/chatbot.sql
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chatbot.sql")

# Para SQLite en memoria o archivo
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        poolclass=StaticPool if DATABASE_URL == "sqlite:///:memory:" else None,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar tablas de BD"""
    Base.metadata.create_all(bind=engine)
