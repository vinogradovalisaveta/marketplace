import os
import uuid

from fastapi import APIRouter, Form, UploadFile
from fastapi.params import Depends, File, Body
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from products.queries import (
    orm_add_product,
    orm_add_new_category,
    orm_get_categories,
    orm_get_products_by_category,
    orm_get_all_products,
    orm_get_product_by_id,
    orm_delete_product,
    orm_update_product,
)

from products.schemas import ProductUpdate


router = APIRouter(tags=["products"])


@router.post("/{add-new-product}")
async def add_new_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    images: list[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
):
    data = {
        "name": name,
        "description": description,
        "price": price,
        "stock": stock,
        "category_id": category_id,
    }
    image_paths = []
    for image in images:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        file_path = f"images/{filename}"
        os.makedirs("images", exist_ok=True)
        with open(file_path, "wb") as buffer:
            contents = await image.read()
            buffer.write(contents)
        image_paths.append(file_path)

    new_product = await orm_add_product(session, data, image_paths)
    return new_product


@router.patch("/{product.id}")
async def update_product(
    product_id: int,
    data_to_update: ProductUpdate = Body(...),
    session: AsyncSession = Depends(get_session),
):
    return await orm_update_product(session, product_id, data_to_update)


@router.get("/{product.id}")
async def get_product_by_id(
    product_id: int, session: AsyncSession = Depends(get_session)
):
    product = await orm_get_product_by_id(session, product_id)
    return product


@router.get("/{category.name}")
async def get_products_by_category(
    category_id: int, session: AsyncSession = Depends(get_session)
):
    products = await orm_get_products_by_category(session, category_id)
    return {"products": products}


@router.get("/all-products")
async def get_all_products(session: AsyncSession = Depends(get_session)):
    products = await orm_get_all_products(session)
    return {"products": products}


@router.delete("/delete-{product.id}")
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return await orm_delete_product(session, product_id)


@router.post("/add-new-category")
async def add_new_category(
    category_name: str, session: AsyncSession = Depends(get_session)
):
    new_category = await orm_add_new_category(session, category_name)
    return new_category


@router.get("/all-categories")
async def get_categories(session: AsyncSession = Depends(get_session)):
    categories = await orm_get_categories(session)
    return {"categories": categories}
