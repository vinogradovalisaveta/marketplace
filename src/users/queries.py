from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.schemas import UserCreateSchema
from users.models import User
from users.password import get_password_hash


async def orm_add_new_user(user_data: UserCreateSchema, session: AsyncSession):
    new_user = User(**user_data.model_dump())
    new_user.password = await get_password_hash(new_user.password)

    session.add(new_user)
    await session.flush()
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def orm_get_all_users(session: AsyncSession):
    query = select(User)
    users = await session.execute(query)
    return users.scalars().all()


async def orm_get_user_by_id(user_id: int, session: AsyncSession):
    query = select(User).where(User.id == user_id)
    user = await session.execute(query)
    return user.scalar_one()
