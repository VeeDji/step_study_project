from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional

from datetime import datetime


class Category(BaseModel):
    """
    Category GET model
    """
    id: int = Field(description="Unique category ID")
    name: str = Field(description="Category name")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    is_active: bool = Field(description="Is active")

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    """
    Category POST/PUT model
    """
    name: str = Field(min_length=3, max_length=50, description="Category name (3-50 characters)")
    parent_id: Optional[int] = Field(None, description="Parent category id if exists")


class Product(BaseModel):
    """
    Product GET model
    """
    id: int = Field(description="Unique product ID")
    name: str = Field(description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(description="Product price")
    image_url: Optional[str] = Field(None, description="Product image URL")
    stock: int = Field(description="Product stock")
    rating: Optional[float] = Field(description="Product grade")
    category_id: int = Field(None, description="Category ID")
    is_active: bool = Field(description="Is active")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Product POST/PUT model
    """
    name: str = Field(min_length=3, max_length=100, description="Product name (3-100 characters)")
    description: Optional[str] = Field(None, max_length=500, description="Product description")
    price: float = Field(gt=0, description="Product price (greater than 0)")
    image_url: Optional[str] = Field(None, max_length=200, description="Product image URL")
    stock: int = Field(gt=0, description="Product stock (0 or greater)")
    category_id: int = Field(description="Category ID for this product")

class UserCreate(BaseModel):
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8, description="Пароль пользователя (минимум 8 символов)")
    role: str = Field(default="buyer", pattern="^(buyer|seller|admin)$", description="Роль пользователя: buyer или seller")

class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)

class ReviewCreate(BaseModel):
    product_id: int = Field(description="Product ID for comment")
    comment: str = Field(max_length=200, description="Comment for product (max 200 characters)")
    grade: int = Field(ge=0, le=5, description="Grade for product (0-5)")

class Review(BaseModel):
    id: int
    user_id: int
    product_id: int
    comment: str
    comment_date: datetime
    grade: int
    is_active: bool