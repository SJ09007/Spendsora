from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary, AnalyticsCharts
from app.services.analytics_service import analytics_service

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return analytics_service.get_summary(db, user_id=current_user.id)

@router.get("/charts", response_model=AnalyticsCharts)
def get_analytics_charts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return analytics_service.get_charts_data(db, user_id=current_user.id)
