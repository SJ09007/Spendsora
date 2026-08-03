from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.category import CategoryResponse

class BudgetBase(BaseModel):
    category_id: int
    amount_limit: float
    period: str = "monthly"

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount_limit: Optional[float] = None
    period: Optional[str] = None

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    spent: float = 0.0
    percentage: float = 0.0
    alert_80_sent: bool
    alert_90_sent: bool
    alert_100_sent: bool
    start_date: datetime
    created_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True
