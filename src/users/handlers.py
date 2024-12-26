from fastapi import APIRouter, HTTPException, status, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from users.schemas import UserCreateSchema, UserUpdateSchema, UserAuthSchema
from users.queries import (
    orm_add_new_user,
    orm_get_all_users,
    orm_get_user_by_id,
    orm_update_user,
    orm_delete_user,
)
from database import get_session

from security.auth import authenticate_user
from security.token import create_access_token, get_current_user

from users.models import User

router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="user_access_token")
    return {"message": "you have been successfully logged out"}


@router.get("/me")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


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


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    session: AsyncSession = Depends(get_session),
):
    user_to_update = await orm_update_user(user_id, user_data, session)
    return user_to_update


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    return await orm_delete_user(user_id, session)


@router.post("/login")
async def auth_user(
    response: Response,
    user_data: UserAuthSchema,
    session: AsyncSession = Depends(get_session),
):
    check = await authenticate_user(
        username=user_data.username, password=user_data.password, session=session
    )
    if check is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong username or password",
        )

    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="user_access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": None}
