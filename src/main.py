from fastapi import FastAPI

from cart.handlers import router as cart_router
from products.handlers import router as product_router
from users.handlers import router as user_router


app = FastAPI()

app.include_router(cart_router)
app.include_router(product_router)
app.include_router(user_router)
