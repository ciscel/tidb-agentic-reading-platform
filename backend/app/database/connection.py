from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

# Create a SQLAlchemy engine using the database URL from our config
connect_args = {}
if settings.TIDB_SSL_CA_PATH:
    connect_args["ssl"] = {"ca": settings.TIDB_SSL_CA_PATH}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Create a SessionLocal class, which is a session factory
# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base, which our models will inherit from
Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
