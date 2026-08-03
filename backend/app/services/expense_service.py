from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, or_, desc
from app.models.expense import Expense
from app.models.category import Category
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.categorization_service import categorization_service

class ExpenseService:
    def create_expense(self, db: Session, user_id: int, expense_in: ExpenseCreate) -> Expense:
        # Check if category exists or map if needed
        category_id = expense_in.category_id
        if not category_id:
            # Get default system category "Miscellaneous"
            cat = db.query(Category).filter(Category.name == "Miscellaneous").first()
            if cat:
                category_id = cat.id

        db_expense = Expense(
            user_id=user_id,
            category_id=category_id,
            amount=expense_in.amount,
            description=expense_in.description,
            merchant=expense_in.merchant,
            date=expense_in.date or datetime.utcnow(),
            payment_mode=expense_in.payment_mode,
            raw_telegram_text=expense_in.raw_telegram_text,
            confidence_score=expense_in.confidence_score or 1.0
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense

    def log_natural_language_expense(self, db: Session, user_id: int, text: str) -> Expense:
        """Parses natural language string and creates expense record."""
        parsed = categorization_service.parse_and_categorize(text)
        
        # Find category by name
        cat_name = parsed["category"]
        category = db.query(Category).filter(
            or_(
                Category.name.ilike(cat_name),
                Category.name == "Miscellaneous"
            )
        ).first()

        category_id = category.id if category else None

        db_expense = Expense(
            user_id=user_id,
            category_id=category_id,
            amount=parsed["amount"],
            description=parsed["description"],
            merchant=parsed["merchant"],
            date=datetime.utcnow(),
            payment_mode=parsed["payment_mode"],
            raw_telegram_text=text,
            confidence_score=parsed["confidence_score"]
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense

    def get_expenses(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[Expense], int]:
        query = db.query(Expense).filter(Expense.user_id == user_id)

        if category_id:
            query = query.filter(Expense.category_id == category_id)

        if search:
            query = query.filter(
                or_(
                    Expense.description.ilike(f"%{search}%"),
                    Expense.merchant.ilike(f"%{search}%"),
                    Expense.raw_telegram_text.ilike(f"%{search}%")
                )
            )

        if start_date:
            query = query.filter(Expense.date >= start_date)

        if end_date:
            query = query.filter(Expense.date <= end_date)

        total = query.count()
        items = query.order_by(desc(Expense.date)).offset(skip).limit(limit).all()
        return items, total

    def update_expense(self, db: Session, expense_id: int, user_id: int, update_in: ExpenseUpdate) -> Optional[Expense]:
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
        if not expense:
            return None

        update_data = update_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        expense.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(expense)
        return expense

    def delete_expense(self, db: Session, expense_id: int, user_id: int) -> bool:
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
        if not expense:
            return False
        db.delete(expense)
        db.commit()
        return True

expense_service = ExpenseService()
