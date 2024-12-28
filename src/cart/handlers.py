from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cart.queries import orm_get_cart, orm_add_product_to_cart
from database import get_session
from security.token import get_current_user
from users.models import User

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/")
async def get_cart(
    session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)
):
    cart = await orm_get_cart(session, user.id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart not found"
        )

    return cart


@router.post("/add")
async def add_product_to_cart(
    product_id: int,
    quantity: int = 1,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    cart = await orm_add_product_to_cart(session, user.id, product_id, quantity)
    return cart
