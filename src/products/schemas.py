from pydantic import BaseModel


class ProductResponse(BaseModel):
    name: str
    description: str
    price: float


class ListProductResponse(BaseModel):
    products: list[ProductResponse]


class CategoryResponse(BaseModel):
    name: str


class ListCategoryResponse(BaseModel):
    categories: list[CategoryResponse]
