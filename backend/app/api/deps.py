"""FastAPI dependency injectors."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

# Type alias for dependency-injected DB session
DB = Annotated[AsyncSession, Depends(get_db)]
