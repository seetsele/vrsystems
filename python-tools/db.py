import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///" + os.path.join(os.path.dirname(__file__), "test_results.db")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_engine():
    return engine

def get_session():
    return SessionLocal()
