from fastapi import Request, HTTPException, status, Depends
from datetime import datetime, timezone, timedelta

from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from users.queries import orm_get_user_by_id

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_auth_data():
    return {"secret_key": SECRET_KEY, "algorithm": ALGORITHM}


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        to_encode, auth_data["secret_key"], algorithm=auth_data["algorythm"]
    )
    return encode_jwt


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
