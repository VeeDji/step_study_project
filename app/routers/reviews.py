import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List

from sqlalchemy.sql.functions import current_user

from app.config import SECRET_KEY, ALGORITHM
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.models.products import Product as ProductModel
from app.db_depends import get_db, get_async_db
from app.schemas import Review as ReviewSchema, ReviewCreate as ReviewCreateSchema
from app.auth import get_current_user
from app.routers.utils import update_product_rating

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

@router.get("/", response_model=List[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Return all reviews
    """
    review = await db.scalars(
        select(ReviewModel).where(ReviewModel.is_active == True)
    )

    return review.all()

async def count_product_rating(product_id: int, db: AsyncSession):
    new_rating = await db.scalar(
        select(func.avg(ReviewModel.grade)).where(ReviewModel.product_id == product_id)
    )
    return new_rating

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
        review: ReviewCreateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_user)
):

    if current_user.role != "buyer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only buyers can create reviews")

    product = await db.scalars(
        select(ProductModel).where(ProductModel.is_active == True, ProductModel.id == review.product_id)
    )

    product_db = product.first()

    if product_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    review_db = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(review_db)
    await db.commit()
    await db.refresh(review_db)

    await update_product_rating(product_db.id, db)

    return review_db

@router.delete("/{review_id}", response_model=ReviewSchema, status_code=status.HTTP_200_OK)
async def delete_review(
        review_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete reviews")


    review = await db.scalars(
        select(ReviewModel)
        .where(
            ReviewModel.is_active == True,
            ReviewModel.id == review_id)
    )
    review_db = review.first()

    if review_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    await db.execute(
        update(ReviewModel)
        .where(ReviewModel.id == review_db.id)
        .values(is_active=False)
    )
    await db.commit()

    await update_product_rating(review_db.product_id, db)

    return review_db