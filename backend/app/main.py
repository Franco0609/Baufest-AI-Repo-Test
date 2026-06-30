from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

ACCESS_TOKEN_EXPIRE_SECONDS = 300
REFRESH_TOKEN_EXPIRE_SECONDS = 3600
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS


DEMO_USER = {
    "username": "admin",
    "hashed_password": "$2b$12$kXf36UAup8oGZcwbLPoWF.uRZVSogsi4wqP8D0TGrZkXYSywGGsk6",
}

app = FastAPI(title="Backend JWT API", version="1.0.0")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Backend JWT API is running"}


@app.post("/auth/token", response_model=TokenResponse)
def create_token(payload: TokenRequest) -> TokenResponse:
    if payload.username != DEMO_USER["username"] or not pwd_context.verify(
        payload.password, DEMO_USER["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return TokenResponse(
        access_token=_encode_token(payload.username, "access", ACCESS_TOKEN_EXPIRE_SECONDS),
        refresh_token=_encode_token(payload.username, "refresh", REFRESH_TOKEN_EXPIRE_SECONDS),
    )


@app.post("/auth/refresh", response_model=AccessTokenResponse)
def refresh_token(payload: RefreshRequest) -> AccessTokenResponse:
    try:
        decoded_token = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if decoded_token.get("type") != "refresh" or decoded_token.get("sub") != DEMO_USER["username"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return AccessTokenResponse(
        access_token=_encode_token(decoded_token["sub"], "access", ACCESS_TOKEN_EXPIRE_SECONDS)
    )


def _encode_token(username: str, token_type: str, expires_in_seconds: int) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(seconds=expires_in_seconds)
    return jwt.encode(
        {
            "sub": username,
            "type": token_type,
            "iat": issued_at,
            "exp": expires_at,
            "jti": str(uuid4()),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
