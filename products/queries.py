import asyncio
import os.path

from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from products.models import Product, ProductImage
from products.models import Category

from products.filters import ProductFilter

from exceptions import CategoryNotFound, ProductNotFound


async def orm_get_category_by_id(session: AsyncSession, category_id: int):
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    category = result.scalar_one_or_none()
    if not category:
        raise CategoryNotFound()
    return category


async def orm_add_product(session: AsyncSession, data: dict, images: list[str]):
    """добавляет новый объект в бд"""
    new_product = Product(**data)
    category = await orm_get_category_by_id(session, new_product.category_id)
    if not category:
        raise CategoryNotFound()
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
    result = await session.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise ProductNotFound()
    return product


async def orm_get_products_by_category(
    session: AsyncSession,
    category_id: int,
    limit: int = 10,
    offset: int = 0,
    product_filter: ProductFilter = ProductFilter(),
):
    category = await orm_get_category_by_id(session, category_id)
    if not category:
        raise CategoryNotFound()

    query = select(Product).where(Product.category_id == category_id)
    query = product_filter.filter(query)
    query = query.limit(limit).offset(offset)

    result = await session.execute(query)
    products = result.scalars().all()

    count_query = select(Product).where(Product.category_id == category_id)
    count_result = await session.execute(count_query)
    total = len(count_result.scalars().all())

    return products, total


async def orm_get_all_products(
    session: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    product_filter: Filter = ProductFilter(),
):
    query = select(Product)
    query = product_filter.filter(query)
    query = query.limit(limit).offset(offset)

    result = await session.execute(query)
    products = result.scalars().all()

    count_query = select(Product)
    count_result = await session.execute(count_query)
    total = len(count_result.scalars().all())

    return products, total


async def orm_update_product(session: AsyncSession, product_id: int, data_to_update):
    product = await orm_get_product_by_id(session, product_id)
    for key, value in data_to_update.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await session.commit()
    await session.refresh(product)
    return product


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
