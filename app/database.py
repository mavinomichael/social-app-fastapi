from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings
import time

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:' \
                          f'{settings.database_password}@{settings.database_hostname}:' \
                          f'{settings.database_port}/{settings.database_name}'
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# sample code to connect to postgresql db without sqlalchemy
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='social', user='postgres', password='6085',
#                                 cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("database connection was successful")
#         break
#     except Exception as error:
#         print("connecting to database failed")
#         print("error", error)
#         time.sleep(2)
