from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cart.models import Cart, CartItem
from exceptions import (
    ProductNotFound,
    InsufficientStock,
    CartNotFound,
    CartItemNotFound,
)
from products.models import Product
from products.queries import orm_get_product_by_id


async def orm_checkout(session: AsyncSession, user_id: int):
    cart = await orm_get_cart(session, user_id)
    if not cart:
        raise CartNotFound()

    for item in cart.items:
        product = await session.get(Product, item["product_id"])
        if not product:
            raise ProductNotFound()
        if product.stock < item["quantity"]:
            raise InsufficientStock(
                message=f'not enough stock fot product "{product.name}". available {product.stock}'
            )
        product.stock -= item["quantity"]

    await session.delete(cart)
    await session.commit()


async def orm_get_cart(session: AsyncSession, user_id: int):
    query = select(Cart).where(Cart.user_id == user_id)
    result = await session.execute(query)
    cart = result.scalar_one_or_none()
    if not cart:
        raise CartNotFound()

    query = select(CartItem).where(CartItem.cart_id == cart.id)
    result = await session.execute(query)
    cart_items = result.scalars().all()

    products = []
    for cart_item in cart_items:
        product_data = await session.get(Product, cart_item.product_id)
        products.append(
            {
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity,
                "name": product_data.name,
                "price": product_data.price,
            }
        )
    cart.items = products
    return cart


async def orm_add_product_to_cart(
    session: AsyncSession, user_id: int, product_id: int, quantity: int = 1
):

    product = await orm_get_product_by_id(session, product_id)

    if not product:
        raise ProductNotFound()

    if product.stock < quantity:
        raise InsufficientStock(
            message=f"not enough stock for {product.name}. available: {product.stock}"
        )

    try:
        cart = await orm_get_cart(session, user_id)
    except CartNotFound:
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


async def orm_delete_product_from_cart(
    session: AsyncSession, user_id: int, product_id: int
):
    cart = await orm_get_cart(session, user_id)

    if not cart:
        raise CartNotFound()

    query = select(CartItem).where(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    )
    result = await session.execute(query)
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise CartItemNotFound()

    await session.delete(cart_item)
    await session.commit()

    return cart


async def orm_update_product_quantity_in_cart(
    session: AsyncSession, user_id: int, product_id: int, quantity: int = 1
):
    cart = await orm_get_cart(session, user_id)
    if not cart:
        raise CartNotFound()

    query = select(CartItem).where(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    )
    result = await session.execute(query)
    cart_item = result.scalar_one_or_none()
    if not cart_item:
        raise CartItemNotFound()

    product = await session.get(Product, product_id)
    if not product:
        raise ProductNotFound()
    if product.stock < quantity:
        raise InsufficientStock(
            message=f"not enough stock for {product.name}. available: {product.stock}"
        )

    cart_item.quantity = quantity
    await session.commit()
    return cart
