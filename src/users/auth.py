from sqlalchemy.ext.asyncio import AsyncSession

from users.queries import orm_get_user_by_username

from users.password import verify_password


async def authenticate_user(username: str, password: str, session: AsyncSession):
    user = await orm_get_user_by_username(username, session)
    if (
        not user
        or verify_password(plain_password=password, hashed_password=user.password)
        is False
    ):
        return None
    else:
        return user
