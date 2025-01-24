from fastapi import FastAPI, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware

from jwt_handler import create_token, decode_token
from hashing import generate_password_hash, hash_password, verify_password
from user import create_db, create_tables, insert_user, select_user, update_user


origins = [
    "http://localhost",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
db_engine = create_db('root', '', 'mysql', 'users')
create_tables(db_engine)

ACCESS_TOKEN_EXPIRE = 60 * 30  # 30 minutes
REFRESH_TOKEN_EXPIRE = 60 * 60 * 24 * 7  # 7 days


# authenticate user
def authenticate_user(engine, id: str, password: str):
    user = select_user(engine, id)
    if not user:
        return False
    if not verify_password(password, user.salt, user.password_hash):
        return False
    return user


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
        return {"status": "ok"}
    except Exception as e:
        raise Exception(f"Failed to create user: {e}")


@app.post("/users/login")
def login(id: str, password: str, response: Response):
    try:
        user = authenticate_user(db_engine, id, password)
        if not user:
            raise Exception(f"Failed to login: Invalid credentials")

        access_payload = {"id": user.id, "email": user.email}
        access_token = create_token(access_payload, ACCESS_TOKEN_EXPIRE, "bearer")
        refresh_payload = {"id": user.id}
        refresh_token = create_token(refresh_payload, REFRESH_TOKEN_EXPIRE, "refresh")

        response.set_cookie(key="refresh_token", value=refresh_token.token, httponly=True)

        update_user(db_engine, id, refresh_token.token)
        return access_token
    except Exception as e:
        raise Exception(f"Failed to login: {e}")


@app.post("/users/refresh")
def token_refresh(refresh_token: str = Cookie(None)):
    try:
        current_user = decode_token(refresh_token)
        if not current_user:
            raise Exception(f"Failed to refresh token: Invalid user")

        user = select_user(db_engine, current_user.user_id)
        if not user:
            raise Exception(f"Failed to refresh token: User not found")
        if user.refresh_token != refresh_token:
            raise Exception(f"Failed to refresh token: Invalid refresh token")

        payload = {"id": user.id, "email": user.email}
        new_access_token = create_token(payload, ACCESS_TOKEN_EXPIRE, "bearer")
        return new_access_token
    except Exception as e:
        raise Exception(f"Failed to refresh token: {e}")


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
