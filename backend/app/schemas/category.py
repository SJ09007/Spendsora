from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    icon: str = "folder"
    color: str = "#6366f1"
    type: str = "expense"

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True
