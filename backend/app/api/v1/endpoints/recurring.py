from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.recurring import RecurringExpense
from app.schemas.recurring import RecurringExpenseCreate, RecurringExpenseResponse

router = APIRouter()

@router.get("", response_model=List[RecurringExpenseResponse])
def get_recurring_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return db.query(RecurringExpense).filter(RecurringExpense.user_id == current_user.id).all()

@router.post("", response_model=RecurringExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_recurring_expense(
    rec_in: RecurringExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    rec = RecurringExpense(
        user_id=current_user.id,
        category_id=rec_in.category_id,
        amount=rec_in.amount,
        description=rec_in.description,
        frequency=rec_in.frequency,
        next_due_date=rec_in.next_due_date
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/{recurring_id}")
def delete_recurring_expense(
    recurring_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    rec = db.query(RecurringExpense).filter(RecurringExpense.id == recurring_id, RecurringExpense.user_id == current_user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring expense not found")
    db.delete(rec)
    db.commit()
    return {"message": "Recurring expense deleted successfully"}
