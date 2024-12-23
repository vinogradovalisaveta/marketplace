from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from users.schemas import UserCreateSchema
from users.queries import orm_add_new_user, orm_get_all_users, orm_get_user_by_id
from database import get_session

router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/")
async def add_new_user(
    user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)
):
    new_user = await orm_add_new_user(user_data, session)
    return new_user


@router.get("/")
async def get_all_users(session: AsyncSession = Depends(get_session)):
    return await orm_get_all_users(session)


@router.get("/{user_id}")
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await orm_get_user_by_id(user_id, session)
    return user
