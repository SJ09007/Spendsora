from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    NaturalLanguageExpenseInput
)
from app.services.expense_service import expense_service
from app.services.budget_service import budget_service

router = APIRouter()

@router.get("", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 50,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    items, _ = expense_service.get_expenses(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
        start_date=start_date,
        end_date=end_date
    )
    return items

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    expense = expense_service.create_expense(db, user_id=current_user.id, expense_in=expense_in)
    
    # Trigger budget alert check
    if expense.category_id:
        budget_service.check_and_trigger_budget_alerts(db, user_id=current_user.id, category_id=expense.category_id)

    return expense

@router.post("/parse", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def parse_and_create_expense(
    input_data: NaturalLanguageExpenseInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    expense = expense_service.log_natural_language_expense(db, user_id=current_user.id, text=input_data.text)
    
    if expense.category_id:
        budget_service.check_and_trigger_budget_alerts(db, user_id=current_user.id, category_id=expense.category_id)

    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    update_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    expense = expense_service.update_expense(db, expense_id=expense_id, user_id=current_user.id, update_in=update_in)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    success = expense_service.delete_expense(db, expense_id=expense_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}
