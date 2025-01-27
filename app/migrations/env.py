import os

from user import Base

if __name__ == "__main__":
    username = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    db = os.getenv("MYSQL_DATABASE")
    DATABASE_URL = f"mysql+pymysql://{username}:{password}@db:3306/{db}"

    target_metadata = Base.metadata
