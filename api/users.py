from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    primary_key = Column(Integer, primary_key=True)
    id = Column(String(36), unique=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime)


def create_db(user, password, host, db_name):
    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine


def create_tables(engine):
    Base.metadata.create_all(engine)
