from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.schemas import UserCreateSchema, UserUpdateSchema
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


async def orm_get_user_by_username(username: str, session: AsyncSession):
    query = select(User).where(User.username == username)
    user = await session.execute(query)
    return user.scalar_one()


async def orm_update_user(
    user_id: int, user_data: UserUpdateSchema, session: AsyncSession
):
    user_to_update = await orm_get_user_by_id(user_id, session)
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user_to_update, key, value)

    await session.commit()
    await session.refresh(user_to_update)
    return user_to_update


async def orm_change_password(user_id: int, new_password: str, session: AsyncSession):
    pass


async def orm_delete_user(user_id: int, session: AsyncSession):
    user = await orm_get_user_by_id(user_id, session)
    await session.delete(user)
    await session.commit()
    return f"{user.username}'s profile was successfully deleted"
