from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from config.models import User
from src.auth.password_utils import verify_password
from src.auth.repos import UserRepository
from src.auth.schemas import UserCreate, UserResponse, Token

from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_access_token, get_current_user,
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    existing_user = await user_repo.get_user_by_email(user_create.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already in use")
    user = await user_repo.create_user(user_create)
    return UserResponse(username=user.username, email=user.email, id=user.id)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.get('/user/me')
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh_token", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    token_data = decode_access_token(refresh_token)
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_username(token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.get('/user/{user_id}')
async def get_user_by_id(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    user_repos = UserRepository(db)
    user = await user_repos.get_user_by_id(user_id)
    return user

