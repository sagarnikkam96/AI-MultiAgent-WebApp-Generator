from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False}, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
