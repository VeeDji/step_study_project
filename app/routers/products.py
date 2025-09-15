from itertools import product

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from typing import List

from app.models import Product as ProductModel, Category as CategoryModel
from app.db_depends import get_db, get_async_db
from app.schemas import Product as ProductSchema, ProductCreate, Review as ReviewSchema
from app.models.users import User as UserModel
from app.models.reviews import Review as ReviewModel
from app.auth import get_current_seller


router = APIRouter(
    prefix="/products",
    tags=["products"],
)



@router.get("/", response_model=List[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Return all products
    """
    product_stmt = select(ProductModel).where(ProductModel.is_active == True).order_by(ProductModel.id)
    product_crtn = await db.scalars(product_stmt)
    product_db = product_crtn.all()
    return product_db


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller)
):
    """
    Create a new product
    """

    category_stmt = select(CategoryModel).where(CategoryModel.id == product.category_id)
    category_crtn = await db.scalars(category_stmt)
    if category_crtn.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return db_product


@router.get("/category/{category_id}", response_model=List[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Return all products by category
    """
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    category_crtn = await db.scalars(category_stmt)
    if category_crtn.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    product_stmt = select(ProductModel).where(and_(ProductModel.category_id == category_id, ProductModel.is_active == True))
    product_crtn = await db.scalars(product_stmt)
    products_db = product_crtn.all()
    return products_db


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Return product stub
    """
    product_stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product_crtn = await db.scalars(product_stmt)
    product_db = product_crtn.first()
    if product_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product_db

@router.get("/{product_id}/reviews", response_model=List[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)):

    product = await db.scalars(
        select(ProductModel)
        .options(selectinload(ProductModel.reviews))
        .where(ProductModel.is_active == True, ProductModel.id == product_id)
    )

    product_db = product.first()

    if product_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product_db.reviews


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(
        product_id: int,
        product: ProductCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserModel = Depends(get_current_seller),
):
    """
    Update product stub
    """
    product_stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product_crtn = await db.scalars(product_stmt)
    product_db = product_crtn.first()
    if product_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product_db.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")

    category_stmt = select(CategoryModel).where(CategoryModel.id == product.category_id)
    category_crtn = await db.scalars(category_stmt)
    if category_crtn.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(product_db)

    return product_db


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)
):
    """
    Delete product stub
    """

    product_stmt = select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    product_crtn = await db.scalars(product_stmt)
    product_db = product_crtn.first()
    if product_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product_db.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
    )
    await db.commit()

    return {"message": "Review deleted"}