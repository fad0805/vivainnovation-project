from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Cookie, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from jwt_handler import create_token, decode_token
from hashing import generate_password_hash, hash_password, verify_password
from post import mongo_init, insert_post, select_post, select_all_posts, update_post, delete_post
from user import mysql_init, insert_user, select_user, update_user

origins = [
    "http://localhost",
]
ACCESS_TOKEN_EXPIRE = 60 * 30  # 30 minutes
REFRESH_TOKEN_EXPIRE = 60 * 60 * 24 * 7  # 7 days

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# db connection
mysql_engine = mysql_init()
mongo_collection = mongo_init()

# authenticate user
def authenticate_user(engine, id: str, password: str):
    user = select_user(engine, id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found: User not found")
    if not verify_password(password, user.salt, user.password_hash):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


# health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# users
@app.post("/users/signup")
def signup(user_info: dict):
    if not user_info:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    id, email, password, created_at = user_info.values()

    salt = generate_password_hash()
    password_hash = hash_password(password, salt)

    try:
        user = select_user(mysql_engine, id)
        if user:
            raise HTTPException(status_code=409, detail="Conflict: User already exists")

        insert_user(mysql_engine, id, email, salt, password_hash, created_at)
        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to signup: {e}")


@app.post("/users/login")
def login(id: str, password: str, response: Response):
    if not id or not password:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    try:
        user = authenticate_user(mysql_engine, id, password)
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        access_payload = {"id": user.id, "email": user.email}
        access_token = create_token(access_payload, ACCESS_TOKEN_EXPIRE, "bearer")
        refresh_payload = {"id": user.id}
        refresh_token = create_token(refresh_payload, REFRESH_TOKEN_EXPIRE, "refresh")

        response.set_cookie(
            key="refresh_token", value=refresh_token.token, httponly=True
        )

        update_user(mysql_engine, id, refresh_token.token)
        return access_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to login: {e}")


@app.post("/users/refresh")
def token_refresh(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Bad Request")

    try:
        current_user = decode_token(refresh_token)
        if not current_user:
            raise Exception(f"Failed to refresh token: Invalid user")

        user = select_user(mysql_engine, current_user.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Not Found: User not found")
        if user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        payload = {"id": user.id, "email": user.email}
        new_access_token = create_token(payload, ACCESS_TOKEN_EXPIRE, "bearer")
        return new_access_token
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh token: {e}")


@app.post("/users/logout")
def logout(response: Response):
    try:
        update_user(mysql_engine, id, None)
        response.delete_cookie(key="refresh_token")
        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to logout: {e}")


# posts
@app.post("/posts")
async def create_post(request: Request):
    if not request.body:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    try:
        access_token = request.headers.get("Authorization")
        post_info = await request.json()
        if access_token is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not post_info.get("title") \
            or not post_info.get("content") \
            or not post_info.get("author_id"):
            raise HTTPException(status_code=422, detail="Unprocessable Entity")

        current_user = decode_token(access_token.split(" ")[1])
        now = datetime.now(timezone.utc)

        if not current_user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if current_user.user_id != post_info["author_id"]:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if not select_user(mysql_engine, current_user.user_id):
            raise HTTPException(status_code=401, detail="Unauthorized")
        if current_user.exp.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(status_code=401, detail="Unauthorized")

        post_info["created_at"] = datetime.now(ZoneInfo("Asia/Seoul"))
        post_id = insert_post(mongo_collection, post_info)
        return {"post_id": str(post_id), "status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create post: {e}")


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    if not post_id:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    try:
        post = select_post(mongo_collection, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Not Found: Post not found")

        return {
            "title": post["title"],
            "content": post["content"],
            "author_id": post["author_id"],
            "created_at": post["created_at"],
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get post: {e}")

@app.get("/posts")
def get_posts(page: int = 1, page_size: int = 10, author_id: str = ''):
    try:
        posts = select_all_posts(mongo_collection, page, page_size, author_id)
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get posts: {e}")


@app.put("/posts/{post_id}")
def to_update_post(post_id: int, post_info: dict, request: Request):
    if not post_id or not post_info:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    try:
        access_token = request.headers.get("Authorization")
        if access_token is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if not post_info.get("title") \
            or not post_info.get("content") \
            or not post_info.get("author_id"):
            raise HTTPException(status_code=422, detail="Unprocessable Entity")

        current_user = decode_token(access_token.split(" ")[1])
        now = datetime.now(timezone.utc)
        original_post = select_post(mongo_collection, post_id)

        if not original_post:
            raise HTTPException(status_code=404, detail="Not Found: Post not found")
        if not current_user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if current_user.user_id != original_post["author_id"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        if current_user.exp.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(status_code=401, detail="Unauthorized")

        updated_post = update_post(mongo_collection, post_id, post_info)
        if updated_post.modified_count == 0:
            raise HTTPException(status_code=400, detail="Bad Request: No changes")

        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update post: {e}")


@app.delete("/posts/{post_id}")
def to_delete_post(post_id: int, request: Request):
    if not post_id:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    try:
        access_token = request.headers.get("Authorization")
        if access_token is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        current_user = decode_token(access_token.split(" ")[1])
        now = datetime.now(timezone.utc)
        post_info = select_post(mongo_collection, post_id)

        if not post_info:
            raise HTTPException(status_code=404, detail="Not Found: Post not found")
        if not current_user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if current_user.user_id != post_info["author_id"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        if current_user.exp.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(status_code=401, detail="Unauthorized")

        delete_post(mongo_collection, post_id)
        return {"status": "ok"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {e}")
