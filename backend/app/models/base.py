from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # obrigatório para Neon serverless
)

def get_session():
    with Session(engine) as session:
        yield session