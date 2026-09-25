from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base
from bot.config import DATABASE_URL

_engine_kwargs = {'echo': False}
if DATABASE_URL.startswith('sqlite'):
    _engine_kwargs['connect_args'] = {'check_same_thread': False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _add_sqlite_column_if_missing(table: str, column: str, definition: str) -> None:
    inspector = inspect(engine)
    columns = {item['name'] for item in inspector.get_columns(table)} if inspector.has_table(table) else set()
    if column not in columns:
        with engine.begin() as connection:
            connection.execute(text(f'ALTER TABLE {table} ADD COLUMN {column} {definition}'))


def init_db():
    """Create tables and safely migrate new SQLite columns."""
    Base.metadata.create_all(bind=engine)
    _add_sqlite_column_if_missing('profiles', 'training_days_per_week', 'INTEGER')
    _add_sqlite_column_if_missing('profiles', 'sleep_hours', 'FLOAT')
    _add_sqlite_column_if_missing('users', 'phone_number', 'VARCHAR(32)')
    print("✅ База данных инициализирована")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
