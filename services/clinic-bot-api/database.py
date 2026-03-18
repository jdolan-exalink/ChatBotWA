import os
from sqlalchemy import create_engine, event, text, inspect
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

SCHEMA_VERSION_TABLE = "schema_version"
TARGET_SCHEMA_VERSION = 6

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_sqlite_parent_dir() -> None:
    """Crea el directorio de la DB sqlite si no existe."""
    if not DATABASE_URL.startswith("sqlite:///"):
        return
    sqlite_path = DATABASE_URL.replace("sqlite:///", "", 1)
    parent = os.path.dirname(sqlite_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _ensure_schema_version_table() -> None:
    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA_VERSION_TABLE} (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text(f"""
            INSERT INTO {SCHEMA_VERSION_TABLE} (id, version)
            SELECT 1, 0
            WHERE NOT EXISTS (SELECT 1 FROM {SCHEMA_VERSION_TABLE} WHERE id = 1)
        """))


def _get_schema_version() -> int:
    _ensure_schema_version_table()
    with engine.begin() as conn:
        row = conn.execute(
            text(f"SELECT version FROM {SCHEMA_VERSION_TABLE} WHERE id = 1")
        ).fetchone()
        return int(row[0]) if row else 0


def _set_schema_version(version: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                f"UPDATE {SCHEMA_VERSION_TABLE} "
                "SET version = :version, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = 1"
            ),
            {"version": int(version)},
        )


def _table_exists(table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return False
    cols = {c["name"] for c in inspector.get_columns(table_name)}
    return column_name in cols


def _add_column_if_missing(table_name: str, column_name: str, ddl_fragment: str) -> None:
    if not _column_exists(table_name, column_name):
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl_fragment}"))


def _migration_v1_bot_config_columns() -> None:
    """Completa columnas historicamente agregadas en bot_config."""
    if not _table_exists("bot_config"):
        return

    migrations = [
        ("timezone", "timezone VARCHAR(50) DEFAULT 'America/Argentina/Buenos_Aires'"),
        ("handoff_enabled", "handoff_enabled BOOLEAN DEFAULT 1"),
        (
            "handoff_message",
            "handoff_message TEXT DEFAULT 'Listo, recibimos tu solicitud. Un operador te contacta a la brevedad.'",
        ),
        ("handoff_inactivity_minutes", "handoff_inactivity_minutes INTEGER DEFAULT 120"),
        (
            "waiting_agent_message",
            "waiting_agent_message TEXT DEFAULT 'Estamos buscando un operador disponible. Por favor aguarda...'",
        ),
        ("in_agent_message", "in_agent_message TEXT DEFAULT 'Un operador esta atendiendo tu solicitud.'"),
        ("closed_message", "closed_message TEXT DEFAULT 'Gracias por contactarte. Tu caso esta cerrado.'"),
        ("debug_mode", "debug_mode BOOLEAN DEFAULT 0"),
        ("sat_opening_time", "sat_opening_time VARCHAR(5) DEFAULT '10:00'"),
        ("sat_closing_time", "sat_closing_time VARCHAR(5) DEFAULT '14:00'"),
        ("sat_enabled", "sat_enabled BOOLEAN DEFAULT 1"),
        ("sun_enabled", "sun_enabled BOOLEAN DEFAULT 0"),
    ]
    for col, ddl in migrations:
        _add_column_if_missing("bot_config", col, ddl)


def _migration_v2_conversation_and_runtime() -> None:
    """Completa columnas nuevas de handoff/runtime en tablas existentes."""
    if _table_exists("conversation_states"):
        cols = [
            ("human_mode", "human_mode BOOLEAN DEFAULT 0"),
            ("human_mode_expire", "human_mode_expire DATETIME"),
            ("assigned_agent_id", "assigned_agent_id INTEGER"),
            ("assigned_agent_name", "assigned_agent_name VARCHAR(255)"),
            ("ticket_id", "ticket_id VARCHAR(100)"),
            ("last_bot_menu", "last_bot_menu VARCHAR(100)"),
            ("extra_data", "extra_data TEXT"),
        ]
        for col, ddl in cols:
            _add_column_if_missing("conversation_states", col, ddl)

    if _table_exists("ticket_history"):
        cols = [
            ("menu_section", "menu_section VARCHAR(100)"),
            ("operator_reply", "operator_reply TEXT"),
        ]
        for col, ddl in cols:
            _add_column_if_missing("ticket_history", col, ddl)


def _migration_v3_external_integrations() -> None:
    """Asegura tabla/columnas para integraciones externas por API key."""
    # create_all ya crea tabla si no existe; esto cubre casos legacy
    Base.metadata.create_all(bind=engine)

    if _table_exists("external_access_tokens"):
        cols = [
            ("name", "name VARCHAR(255)"),
            ("token_prefix", "token_prefix VARCHAR(32)"),
            ("token_hash", "token_hash VARCHAR(128)"),
            ("description", "description TEXT"),
            ("allowed_event_types", "allowed_event_types VARCHAR(255) DEFAULT '*'"),
            ("is_active", "is_active BOOLEAN DEFAULT 1"),
            ("created_by", "created_by VARCHAR(255)"),
            ("last_used_at", "last_used_at DATETIME"),
            ("created_at", "created_at DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "updated_at DATETIME"),
        ]
        for col, ddl in cols:
            _add_column_if_missing("external_access_tokens", col, ddl)

def _migration_v4_ticket_fields() -> None:
    if _table_exists("conversation_states"):
        _add_column_if_missing("conversation_states", "ticket_status", "ticket_status VARCHAR(50) DEFAULT 'pendiente'")

    if _table_exists("ticket_history"):
        cols = [
            ("ticket_status", "ticket_status VARCHAR(50) DEFAULT 'cerrado'"),
            ("is_deleted", "is_deleted BOOLEAN DEFAULT 0"),
            ("deleted_by", "deleted_by VARCHAR(255)"),
        ]
        for col, ddl in cols:
            _add_column_if_missing("ticket_history", col, ddl)


def _migration_v5_scheduled_date() -> None:
    """Agrega columna send_date a scheduled_messages para mensajes de fecha específica."""
    if _table_exists("scheduled_messages"):
        _add_column_if_missing(
            "scheduled_messages", "send_date",
            "send_date VARCHAR(10) DEFAULT NULL"
        )


def _migration_v6_ticket_breadcrumb() -> None:
    """Agrega columna menu_breadcrumb para historial y estado actual."""
    if _table_exists("conversation_states"):
        _add_column_if_missing("conversation_states", "menu_breadcrumb", "TEXT")
    if _table_exists("ticket_history"):
        _add_column_if_missing("ticket_history", "menu_breadcrumb", "TEXT")


def _run_schema_migrations() -> int:
    migrations = [
        (1, _migration_v1_bot_config_columns),
        (2, _migration_v2_conversation_and_runtime),
        (3, _migration_v3_external_integrations),
        (4, _migration_v4_ticket_fields),
        (5, _migration_v5_scheduled_date),
        (6, _migration_v6_ticket_breadcrumb),
    ]

    current = _get_schema_version()
    for version, fn in migrations:
        if version > current:
            fn()
            _set_schema_version(version)
            current = version
    return current

def init_db():
    """Inicializa DB, crea desde cero si falta y migra schema por versión."""
    _ensure_sqlite_parent_dir()
    Base.metadata.create_all(bind=engine)
    final_version = _run_schema_migrations()
    print(f"[DB] Schema version actual: {final_version}")
