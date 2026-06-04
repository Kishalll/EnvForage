from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services.user_repository import UserRepository

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegData(BaseModel):
    fname: str
    lname: str
    email: EmailStr
    password: str


class LoginData(BaseModel):
    email: EmailStr
    password: str


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/signup")
async def signup(data: RegData, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    repo = UserRepository(db)
    if await repo.user_exists(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")
    await repo.create_user(
        email=data.email,
        fname=data.fname,
        lname=data.lname,
        hashed_password=pwd.hash(data.password),
    )
    return {"message": "Account created successfully"}


@router.post("/signin")
async def signin(data: LoginData, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    repo = UserRepository(db)
    user = await repo.get_user_by_email(data.email)
    if not user or not pwd.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    exp = datetime.now(UTC) + timedelta(hours=24)
    settings = get_settings()
    token = jwt.encode(
        {"email": data.email, "exp": exp}, settings.secret_key, algorithm="HS256"
    )
    return {"token": token, "email": data.email}
