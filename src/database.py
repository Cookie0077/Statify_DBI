from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQL_ALCHEMY_DATABASE_URL = "sqlite:///./statify.db"

engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

Sesionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = Sesionlocal()

    try:
        yield db
    finally:
        db.close()
