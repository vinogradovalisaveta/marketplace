from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cart.queries import (
    orm_get_cart,
    orm_add_product_to_cart,
    orm_delete_product_from_cart,
    orm_update_product_quantity_in_cart,
)
from database import get_session
from security.token import get_current_user
from users.models import User

from cart.queries import ProductNotFound, InsufficientStock

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


@router.post("/add-product")
async def add_product_to_cart(
    product_id: int,
    quantity: int = 1,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        cart = await orm_add_product_to_cart(session, user.id, product_id, quantity)
        return cart
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    except InsufficientStock as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete("/delete-product")
async def delete_product_from_cart(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    cart = await orm_delete_product_from_cart(session, user.id, product_id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart not found"
        )

    return cart


@router.post("/update-quantity")
async def update_product_quantity_in_cart(
    product_id: int,
    quantity: int = 1,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    cart = await orm_update_product_quantity_in_cart(
        session, user.id, product_id, quantity
    )

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart not found"
        )

    return cart
