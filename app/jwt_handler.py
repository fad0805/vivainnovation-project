import os

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel

SECRET_KEY = os.getenv("SECRET_KEY", "no secret key provided")


class Token(BaseModel):
    token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str
    email: str|None = None
    exp: datetime


def create_token(data: dict, expires_in: int, token_type):
    to_encode = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    to_encode.update({"exp": expiration})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return Token(token=encoded_jwt, token_type=token_type)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        id = payload.get("id")
        email = payload.get("email")
        expiration = payload.get("exp")
        if id is None or expiration is None:
            raise JWTError("Could not validate credentials")

        decoded_token = TokenData(user_id=id, email=email, exp=expiration)
        return decoded_token
    except JWTError as e:
        raise JWTError(f"Could not validate credentials: {e}")
