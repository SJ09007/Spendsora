from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.category import CategoryResponse

class ExpenseBase(BaseModel):
    amount: float
    description: str
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None
    payment_mode: str = "UPI"

class ExpenseCreate(ExpenseBase):
    raw_telegram_text: Optional[str] = None
    confidence_score: Optional[float] = 1.0

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[datetime] = None
    payment_mode: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    confidence_score: float
    raw_telegram_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

class NaturalLanguageExpenseInput(BaseModel):
    text: str
