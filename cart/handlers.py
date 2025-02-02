from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cart.queries import (
    orm_add_product_to_cart,
    orm_checkout,
    orm_delete_product_from_cart,
    orm_get_cart,
    orm_update_product_quantity_in_cart,
)
from database import get_session
from exceptions import (
    CartNotFound,
    CartItemNotFound,
    ProductNotFound,
    InsufficientStock,
    UserNotFound,
)
from security.token import get_current_user
from users.models import User


router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/checkout")
async def checkout(
    session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)
):
    try:
        await orm_checkout(session, user.id)
        return {"message": "successfull checkout"}
    except CartNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart not found"
        )
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    except InsufficientStock as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/")
async def get_cart(
    session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)
):
    try:
        cart = await orm_get_cart(session, user.id)
        return cart
    except CartNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart not found"
        )


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
    try:
        cart = await orm_delete_product_from_cart(session, user.id, product_id)
        return cart
    except CartItemNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart item not found"
        )


@router.post("/update-quantity")
async def update_product_quantity_in_cart(
    product_id: int,
    quantity: int = 1,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    try:
        cart = await orm_update_product_quantity_in_cart(
            session, user.id, product_id, quantity
        )
        return cart
    except InsufficientStock as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        )
    except CartNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart not found"
        )
    except CartItemNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="cart item not found"
        )
