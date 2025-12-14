from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# For an MVP with SQLite, the database will be a file in the root directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./prosi_mini.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # connect_args is needed only for SQLite to allow multithreading
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
