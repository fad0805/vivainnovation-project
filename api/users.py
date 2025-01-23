from sqlalchemy import create_engine, Column, Integer, String, DateTime, Sequence, \
    insert
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    primary_key = Column(Integer, Sequence('users_primary_key'), primary_key=True)
    id = Column(String(36), unique=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime)
    refesh_token = Column(String(255), default=None)


def create_db(user, password, host, db_name):
    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine


def create_tables(engine):
    Base.metadata.create_all(engine)


def insert_user(engine, id, email, password_hash, created_at):
    insert_stmt = insert(Users).values(id=id, email=email, password_hash=password_hash, created_at=created_at)
    with engine.connect() as connection:
        connection.execute(insert_stmt)
        connection.commit()
