from fastapi import Depends, status, HTTPException
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.auth.schemas import TokenData
from src.auth.repos import UserRepository
from config.models import User
from config.general import settings
from config.db import get_db

ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
VERIFICATION_TOKEN_EXPIRE_HOURS = settings.verification_token_expire_hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encode_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encode_jwt


def decode_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_cookies(request, db: AsyncSession):
    token = request.cookies.get("access_token")
    if token:
        user_data = decode_access_token(token)
    else:
        return None
    if user_data is not None:
        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_username(user_data.username)
    else:
        return None

    return user
