from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.insight import AIInsightResponse
from app.services.ai_insight_service import ai_insight_service

router = APIRouter()

@router.get("", response_model=List[AIInsightResponse])
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return ai_insight_service.generate_insights(db, user_id=current_user.id)
