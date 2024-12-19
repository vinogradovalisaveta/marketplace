from typing import List

from sqlalchemy import Integer, String, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    category: Mapped['Category'] = relationship(backref='products')
    images: Mapped[List['ProductImage']] = relationship(backref='product', lazy="dynamic")


class ProductImage(Base):
    __tablename__ = 'product_images'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    image_url: Mapped[str] = mapped_column(String)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
