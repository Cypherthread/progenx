from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
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
    """Create tables if they don't exist, and add missing columns to existing tables.
    This handles the case where new columns (like stripe_customer_id) are added
    to models but the SQLite database already exists from a previous version."""
    Base.metadata.create_all(bind=engine)

    # Auto-migrate: add missing columns to existing tables
    if "sqlite" in settings.DATABASE_URL:
        _migrate_sqlite()


def _migrate_sqlite():
    """Add missing columns to existing SQLite tables.
    SQLAlchemy's create_all doesn't add columns to existing tables."""
    import sqlite3

    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get existing columns for users table
        cursor.execute("PRAGMA table_info(users)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        # Columns that should exist (added in updates)
        migrations = {
            "users": {
                "stripe_customer_id": "TEXT DEFAULT ''",
                "stripe_subscription_id": "TEXT DEFAULT ''",
            },
        }

        for table, columns in migrations.items():
            for col_name, col_type in columns.items():
                if col_name not in existing_cols:
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                        print(f"[DB] Migrated: added {table}.{col_name}")
                    except sqlite3.OperationalError:
                        pass  # Column might already exist in a race condition

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Migration check failed (non-fatal): {e}")
