from fastapi import FastAPI
from users import create_db, create_tables, insert_user, get_user
import hashlib
import secrets

app = FastAPI()
db_engine = create_db('root', '', 'mysql', 'users')
create_tables(db_engine)


# hashing password
def generate_password_hash():
    return secrets.token_urlsafe(16)

def hash_password(password: str, salt: str):
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_password(password: str, salt: str, password_hash: str):
    return hash_password(password, salt) == password_hash


# health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# users
@app.post("/users/signup")
def signup(user_info: dict):
    id, email, password, created_at = user_info.values()

    salt = generate_password_hash()
    password_hash = hash_password(password, salt)

    try:
        insert_user(db_engine, id, email, salt, password_hash, created_at)
        return True
    except Exception as e:
        print(e)
        return False


@app.post("/users/login")
def login(id: str, password: str):
    user = get_user(db_engine, id)
    if user:
        return verify_password(password, user.salt, user.password_hash)
    return False


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
