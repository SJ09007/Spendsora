from typing import Any
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.services.export_service import export_service

router = APIRouter()

@router.get("/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    csv_data = export_service.export_to_csv(db, user_id=current_user.id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=expenses_{current_user.id}.csv"}
    )
