from fastapi import FastAPI
from users import create_db, create_tables, insert_user

app = FastAPI()
db_engine = create_db('root', '', 'mysql', 'users')
create_tables(db_engine)


# users
@app.post("/users/signup")
def signup(user_info: dict):
    id, email, password_hash, created_at = user_info.values()
    try:
        insert_user(db_engine, id, email, password_hash, created_at)
        return True
    except Exception as e:
        print(e)
        return False


@app.post("/users/login")
def login():
    pass


@app.post("/users/refresh")
def token_refresh():
    pass


@app.post("/users/logout")
def logout():
    pass


# posts
@app.post("/posts")
def create_post():
    pass


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    pass


@app.get("/posts")
def get_posts():
    pass


@app.put("/posts/{post_id}")
def update_post(post_id: int):
    pass


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    pass
