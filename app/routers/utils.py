from sqlalchemy.sql import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel

async def update_product_rating(product_id: int, db: AsyncSession):
    result = await db.execute(
            select(func.avg(ReviewModel.grade))
            .where(
                ReviewModel.product_id == product_id,
                ReviewModel.is_active == True
            )
        )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()