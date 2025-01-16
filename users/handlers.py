from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Response
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from exceptions import UserNotFound
from security.auth import authenticate_user
from security.token import (
    create_access_token,
    get_current_user,
    create_refresh_token,
    get_refresh_token_from_db,
    delete_refresh_token_from_db,
)
from users.models import User
from users.schemas import UserCreateSchema, UserUpdateSchema, UserAuthSchema
from users.queries import (
    orm_add_new_user,
    orm_get_all_users,
    orm_get_user_by_id,
    orm_update_user,
    orm_delete_user,
)


router = APIRouter(prefix="/auth", tags=["users"])


@router.post("/logout")
async def logout_user(
    response: Response,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if user:
        await delete_refresh_token_from_db(user.id, session)

        response.delete_cookie(key="user_access_token")
        response.delete_cookie(key="user_refresh_token")
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
    try:
        user = await orm_get_user_by_id(user_id, session)
        return user
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    session: AsyncSession = Depends(get_session),
):
    try:
        user_to_update = await orm_update_user(user_id, user_data, session)
        return user_to_update
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    try:
        return await orm_delete_user(user_id, session)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )


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
    refresh_token = await create_refresh_token(check.id, session)
    response.set_cookie(key="user_access_token", value=access_token, httponly=True)
    response.set_cookie(key="user_refresh_token", value=refresh_token, httponly=True)
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/token")
async def refresh_tokens(
    response: Response, refresh_token: str, session: AsyncSession = Depends(get_session)
):
    refresh_token_from_db = await get_refresh_token_from_db(refresh_token, session)

    if not refresh_token_from_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token"
        )

    if refresh_token_from_db.expires_at < datetime.now(timezone.utc):
        await delete_refresh_token_from_db(refresh_token, session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token expired"
        )

    user = await session.get(User, refresh_token_from_db.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = await create_refresh_token(user.id, session)

    await delete_refresh_token_from_db(user.id, session)

    response.set_cookie(key="user_access_token", value=access_token, httponly=True)
    response.set_cookie(
        key="user_refresh_token", value=new_refresh_token, httponly=True
    )
    return {"access_token": access_token, "refresh_token": refresh_token}
