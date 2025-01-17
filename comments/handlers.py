from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from comments.queries import orm_add_new_comment
from database import get_session
from exceptions import UserNotFound, ProductNotFound
from security.token import get_current_user
from users.models import User

router = APIRouter(prefix="/comment", tags=["comments"])


@router.post("/")
async def add_new_comment(
    product_id: int,
    text: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await orm_add_new_comment(user.id, product_id, text, session)
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
