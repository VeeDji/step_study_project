from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List

from app.models.categories import Category as CategoryModel
from app.db_depends import get_db, get_async_db
from app.schemas import Category as CategorySchema, CategoryCreate

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=List[CategorySchema], status_code=status.HTTP_200_OK)
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Get all categories
    """
    category_stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    category_crtn = await db.scalars(category_stmt)
    categories_db = category_crtn.all()
    return categories_db


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Create a new category
    """
    if category.parent_id is not None:
        category_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id)
        category_crtn = await db.scalars(category_stmt)
        category_db =  category_crtn.first()
        if category_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found")

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return db_category

@router.put("/{category_id}", response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def update_category(category_id: int, category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Update a category
    """
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    category_crtn = await db.scalars(category_stmt)
    category_db = category_crtn.first()
    if category_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id)
        parent_crtn = await db.scalars(parent_stmt)
        if parent_crtn.first() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found")

    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump(exclude_unset=True))
    )
    await db.commit()
    await db.refresh(category_db)

    return category_db


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Delete a category
    """
    category_stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    category_crtn = await db.scalars(category_stmt)
    if category_crtn.first() is None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False))
    await db.commit()

    return {"status": "success", "message": "Category marked as inactive"}

