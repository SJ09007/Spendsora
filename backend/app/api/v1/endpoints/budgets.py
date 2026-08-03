from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.services.budget_service import budget_service

router = APIRouter()

@router.get("", response_model=List[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    return budget_service.get_user_budgets_with_spending(db, user_id=current_user.id)

@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_in.category_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Budget for this category already exists.")

    budget = Budget(
        user_id=current_user.id,
        category_id=budget_in.category_id,
        amount_limit=budget_in.amount_limit,
        period=budget_in.period
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    budgets = budget_service.get_user_budgets_with_spending(db, user_id=current_user.id)
    return [b for b in budgets if b["id"] == budget.id][0]

@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}
