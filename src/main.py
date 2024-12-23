from fastapi import FastAPI

from products.handlers import router as products_router
from users.handlers import router as users_router

app = FastAPI()

app.include_router(products_router)
app.include_router(users_router)
