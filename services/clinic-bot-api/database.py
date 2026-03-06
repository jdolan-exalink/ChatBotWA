import os
from sqlalchemy import create_engine, event, text
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
    # WAL mode: permite lecturas concurrentes sin bloquear escrituras
    @event.listens_for(engine, "connect")
    def _set_wal_mode(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")   # 5s wait en lugar de error inmediato
        cursor.close()
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
