from sqlalchemy import create_engine, Column, Integer, String, DateTime, Sequence, \
    insert, select, update
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    primary_key = Column(Integer, Sequence('users_primary_key'), primary_key=True)
    id = Column(String(36), unique=True)
    email = Column(String(255), unique=True)
    salt = Column(String(255))
    password_hash = Column(String(255))
    created_at = Column(DateTime)
    refresh_token = Column(String(510), default=None)


def create_db(user, password, host, db_name):
    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine


def create_tables(engine):
    Base.metadata.create_all(engine)


def insert_user(engine, id, email, salt, password_hash, created_at):
    stmt = insert(User).values(id=id, email=email,
                                salt=salt, password_hash=password_hash,
                                created_at=created_at)
    with engine.connect() as connection:
        connection.execute(stmt)
        connection.commit()


def select_user(engine, id):
    stmt = select(User).where(User.id == id)
    with engine.connect() as connection:
        result = connection.execute(stmt)
        return result.fetchone()

def update_user(engine, id, refresh_token):
    stmt = update(User).where(User.id == id).values(refresh_token=refresh_token)
    with engine.connect() as connection:
        connection.execute(stmt)
        connection.commit()
