from sqlalchemy.ext.asyncio import AsyncSession

from comments.models import Comment
from products.queries import orm_get_product_by_id


async def orm_add_new_comment(
    user_id: int, product_id: int, text: str, session: AsyncSession
) -> Comment:
    product = await orm_get_product_by_id(session, product_id)
    new_comment = Comment(user_id=user_id, product_id=product.id, text=text)
    session.add(new_comment)
    await session.commit()
    return new_comment
