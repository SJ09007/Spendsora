from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.category import CategoryResponse

class RecurringExpenseBase(BaseModel):
    amount: float
    description: str
    category_id: Optional[int] = None
    frequency: str = "monthly"
    next_due_date: datetime

class RecurringExpenseCreate(RecurringExpenseBase):
    pass

class RecurringExpenseResponse(RecurringExpenseBase):
    id: int
    user_id: int
    last_processed_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
