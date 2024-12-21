import asyncio
import os.path

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from products.models import Product, ProductImage
from products.models import Category


async def orm_add_product(session: AsyncSession, data: dict, images: list[str]):
    """добавляет новый объект в бд"""
    new_product = Product(**data)
    session.add(new_product)
    await session.flush()

    for image in images:
        new_image = ProductImage(product_id=new_product.id, image_url=image)
        session.add(new_image)

    await session.commit()
    return new_product


async def orm_get_product_by_id(session: AsyncSession, product_id: int):
    """возвращает товар по его id"""
    query = select(Product).where(Product.id == product_id)
    product = await session.execute(query)
    return product.scalar()


async def orm_get_products_by_category(session: AsyncSession, category_id: int):
    query = select(Product).where(Product.category_id == category_id)
    products = await session.execute(query)
    return products.scalars().all()


async def orm_get_all_products(session: AsyncSession):
    query = select(Product)
    products = await session.execute(query)
    return products.scalars().all()


async def orm_update_product(session: AsyncSession, product_id: int):
    pass


async def orm_delete_product(session: AsyncSession, product_id: int):
    product = await orm_get_product_by_id(session, product_id)
    # if product:
    #     for image in product.images:
    #         file_path = image.image_url
    #         if os.path.exists(file_path):
    #             os.remove(file_path)
    #
    await session.delete(product)
    await session.commit()
    return f'product "{product.name}" was successfully deleted'


async def orm_add_new_category(session: AsyncSession, category_name: str):
    """добавление новой категории"""
    new_category = Category(name=category_name)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category


async def orm_get_categories(session: AsyncSession):
    """возвращает все категории"""
    query = select(Category)
    categories = await session.execute(query)
    return categories.scalars().all()
