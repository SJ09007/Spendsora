from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.services.search_service import search_service

router = APIRouter()

@router.get("")
def search_expenses(
    q: str = Query(..., description="Natural language search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return search_service.execute_natural_search(db, user_id=current_user.id, query_text=q)
