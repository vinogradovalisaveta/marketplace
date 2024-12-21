from fastapi import FastAPI

from products.handlers import router as products_router

app = FastAPI()

app.include_router(products_router)
