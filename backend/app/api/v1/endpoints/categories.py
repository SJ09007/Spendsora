from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter()

@router.get("", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return db.query(Category).filter(
        or_(Category.user_id == current_user.id, Category.is_system == True)
    ).all()

@router.post("", response_model=CategoryResponse)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    category = Category(
        user_id=current_user.id,
        name=category_in.name,
        icon=category_in.icon,
        color=category_in.color,
        type=category_in.type,
        is_system=False
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
