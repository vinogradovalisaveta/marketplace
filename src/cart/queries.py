from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cart.models import Cart, CartItem


async def orm_get_cart(session: AsyncSession, user_id: int):
    query = select(Cart).where(Cart.user_id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def orm_add_product_to_cart(
    session: AsyncSession, user_id: int, product_id: int, quantity: int = 1
):
    cart = await orm_get_cart(session, user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    query = select(CartItem).where(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    )
    result = await session.execute(query)
    cart_item = result.scalar_one_or_none()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        session.add(cart_item)
    await session.commit()
    return cart
