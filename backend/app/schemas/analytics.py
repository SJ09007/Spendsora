from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CategorySpending(BaseModel):
    category_id: Optional[int]
    category_name: str
    icon: str
    color: str
    total_amount: float
    percentage: float
    count: int

class DailySpending(BaseModel):
    date: str
    amount: float

class TopMerchant(BaseModel):
    merchant: str
    amount: float
    count: int

class AnalyticsSummary(BaseModel):
    total_spending: float
    today_spending: float
    weekly_spending: float
    monthly_spending: float
    yearly_spending: float
    avg_per_day: float
    avg_per_transaction: float
    highest_expense: Optional[Dict[str, Any]] = None
    lowest_expense: Optional[Dict[str, Any]] = None
    top_category: Optional[str] = None
    total_transactions: int

class AnalyticsCharts(BaseModel):
    categories: List[CategorySpending]
    daily_trend: List[DailySpending]
    top_merchants: List[TopMerchant]
    payment_modes: List[Dict[str, Any]]
