from uuid import uuid4

from fastapi import Request, HTTPException, status, Depends
from datetime import datetime, timezone, timedelta

from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.queries import orm_get_user_by_id
from security.models import RefreshToken

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def get_auth_data():
    return {"secret_key": SECRET_KEY, "algorithm": ALGORITHM}


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"]
    )
    return encode_jwt


async def create_refresh_token(user_id: int, session: AsyncSession) -> str:
    refresh_token = uuid4()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = RefreshToken(
        token=refresh_token, user_id=user_id, expires_at=expire
    )
    session.add(new_refresh_token)
    await session.commit()
    return str(refresh_token)


async def get_refresh_token_from_db(token: str, session: AsyncSession) -> RefreshToken:
    token_object = await session.get(RefreshToken, token)
    return token_object


async def delete_refresh_token_from_db(user_id: str, session: AsyncSession) -> None:
    query = select(RefreshToken).where(RefreshToken.user_id == user_id)
    result = await session.execute(query)
    token_object = result.scalar_one_or_none()
    if token_object:
        await session.delete(token_object)
        await session.commit()
    # token_object = await session.get(RefreshToken, str(user_id))
    # if token_object:
    #     await session.delete(token_object)
    #     await session.commit()


def get_token(request: Request):
    token = request.cookies.get("user_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token not found"
        )
    return token


async def get_current_user(
    token: str = Depends(get_token), session: AsyncSession = Depends(get_session)
):

    # получаем необходимые данные из токена (айди и время жизни токена)
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(
            token, auth_data["secret_key"], algorithms=[auth_data["algorithm"]]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token not found"
        )

    # проверяем не истек ли токен
    expire = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token not found"
        )

    # проверяем наличие юзера по айди
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token not found"
        )

    user = await orm_get_user_by_id(int(user_id), session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token not found"
        )

    return user
