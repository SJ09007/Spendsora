from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    expenses,
    categories,
    budgets,
    recurring,
    analytics,
    insights,
    search,
    export
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_router.include_router(recurring.router, prefix="/recurring", tags=["Recurring Expenses"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(insights.router, prefix="/insights", tags=["AI Insights"])
api_router.include_router(search.router, prefix="/search", tags=["Natural Language Search"])
api_router.include_router(export.router, prefix="/export", tags=["Exports"])
