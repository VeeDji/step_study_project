import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.config import SECRET_KEY, ALGORITHM
from app.models import User as UserModel
from app.db_depends import get_db, get_async_db
from app.schemas import User as UserSchema, UserCreate as UserCreateSchema
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema, db: AsyncSession = Depends(get_async_db)):

    email_crtn = await db.scalars(
                    select(UserModel.email).where(
                        UserModel.email == user.email
                    )
    )
    if email_crtn.first() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_db = UserModel(
                email=user.email,
                hashed_password=hash_password(user.password),
                role=user.role,
    )

    db.add(user_db)
    await db.commit()
    return user_db

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    """
    Аутентификауия пользователя
    """
    user_crtn = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username)
    )
    user_db = user_crtn.first()

    if not user_db or not verify_password(form_data.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(data={"sub": user_db.email, "role": user_db.role, "id": user_db.id})
    refresh_token = create_refresh_token(data={"sub": user_db.email, "role": user_db.role, "id": user_db.id})
    return {"access_token": access_token, "refreah_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh-token")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_async_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.exceptions:
        raise credentials_exception

    user_crtn = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user_db = user_crtn.first()
    if user_db is None:
        raise credentials_exception
    access_token = create_access_token(data={"sub": user_db.email, "role": user_db.role, "id": user_db.id})
    return {"access_token": access_token, "token_type": "bearer"}