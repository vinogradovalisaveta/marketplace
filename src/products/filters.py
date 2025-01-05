from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from products.models import Product


class ProductFilter(Filter):
    name__ilike: Optional[str] = None
    price__lte: Optional[float] = None
    price__gte: Optional[float] = None

    class Constants(Filter.Constants):
        model = Product
