"""Database configuration and session management"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool if "postgresql" in settings.DATABASE_URL else None,
    pool_size=settings.DB_POOL_SIZE if "postgresql" in settings.DATABASE_URL else 5,
    max_overflow=settings.DB_MAX_OVERFLOW if "postgresql" in settings.DATABASE_URL else 10,
    pool_timeout=settings.DB_POOL_TIMEOUT if "postgresql" in settings.DATABASE_URL else 30,
    pool_recycle=settings.DB_POOL_RECYCLE if "postgresql" in settings.DATABASE_URL else 3600,
    echo=settings.DEBUG,
    connect_args={"connect_timeout": 10} if "postgresql" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure connection on connect"""
    # Only set timezone for PostgreSQL
    if "postgresql" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("SET timezone = 'UTC'")
        cursor.close()
