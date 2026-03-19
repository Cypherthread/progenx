from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

_connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    _connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    pool_size=5 if "postgresql" in settings.DATABASE_URL else 0,
    max_overflow=10 if "postgresql" in settings.DATABASE_URL else 0,
    pool_pre_ping=True,  # test connections before using them
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if they don't exist (including new tables like api_keys,
    design_versions), and add missing columns to existing tables."""
    Base.metadata.create_all(bind=engine)

    # Auto-migrate: add missing columns to existing tables
    if "sqlite" in settings.DATABASE_URL:
        _migrate_sqlite()
    elif "postgresql" in settings.DATABASE_URL:
        _migrate_postgresql()


def _migrate_postgresql():
    """Add missing columns to existing PostgreSQL tables."""
    from sqlalchemy import text

    migrations = {
        "designs": {
            "bump_count": "INTEGER DEFAULT 0",
            "is_public": "BOOLEAN DEFAULT FALSE",
        },
        "users": {
            "stripe_customer_id": "TEXT DEFAULT ''",
            "stripe_subscription_id": "TEXT DEFAULT ''",
            "bump_count": "INTEGER DEFAULT 0",
        },
    }

    try:
        with engine.connect() as conn:
            for table, columns in migrations.items():
                for col_name, col_type in columns.items():
                    try:
                        conn.execute(text(
                            f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                        ))
                        conn.commit()
                        print(f"[DB] Migrated: added {table}.{col_name}")
                    except Exception:
                        conn.rollback()
    except Exception as e:
        print(f"[DB] PostgreSQL migration check failed (non-fatal): {e}")


def _migrate_sqlite():
    """Add missing columns to existing SQLite tables.
    SQLAlchemy's create_all doesn't add columns to existing tables."""
    import sqlite3

    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Columns that should exist (added in updates)
        migrations = {
            "users": {
                "stripe_customer_id": "TEXT DEFAULT ''",
                "stripe_subscription_id": "TEXT DEFAULT ''",
            },
            "designs": {
                "bump_count": "INTEGER DEFAULT 0",
                "is_public": "BOOLEAN DEFAULT 0",
            },
        }

        # Allowlist of safe table and column names
        SAFE_TABLES = {"users", "designs"}
        SAFE_COLUMN_NAMES = {"stripe_customer_id", "stripe_subscription_id", "bump_count", "is_public"}

        for table, columns in migrations.items():
            if table not in SAFE_TABLES:
                continue
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = {row[1] for row in cursor.fetchall()}
            for col_name, col_type in columns.items():
                if col_name not in existing_cols and col_name in SAFE_COLUMN_NAMES:
                    try:
                        # Safe: col_name is from allowlist, not user input
                        stmt = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                        cursor.execute(stmt)
                        print(f"[DB] Migrated: added {table}.{col_name}")
                    except sqlite3.OperationalError:
                        pass

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Migration check failed (non-fatal): {e}")
