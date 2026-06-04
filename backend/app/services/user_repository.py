"""User repository for persistent user account management."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user CRUD operations with database persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def user_exists(self, email: str) -> bool:
        """Check if user with given email exists."""
        result = await self.db.execute(
            select(User).where(User.email == email).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create_user(
        self, email: str, fname: str, lname: str, hashed_password: str
    ) -> User:
        """Create and persist a new user account."""
        user = User(
            email=email,
            fname=fname,
            lname=lname,
            password=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
