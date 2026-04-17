# database.py

import os

import dotenv

"""
Load environment variables (e.g. DB connection string)
"""
dotenv.load_dotenv()

CONNECTION_STRING = os.getenv("DB_URL")

"""
ENGINE

The engine is a factory that knows how to connect to the database.
It does NOT open a connection immediately — it is used by sessions when needed.
"""
from sqlalchemy import create_engine

engine = create_engine(CONNECTION_STRING)

"""
BASE (Schema Registry)

Base is the foundation for all models.
Any model that inherits from Base will be tracked here,
allowing SQLAlchemy to map Python classes to database tables.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""
SESSION FACTORY

SessionLocal is NOT a database session.
It is a factory that creates new session instances (one per request/operation).

Each session represents a conversation with the database
and must be closed after use.
"""
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""
FastAPI dependency that provides a database session per request.

- A new session is created when the request starts
- The session is injected into route functions via Depends(get_db)
- Execution pauses at `yield` and resumes after the request finishes
- The `finally` block ensures the session is always closed,
  returning the connection to the pool (even if an error occurs)
"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
