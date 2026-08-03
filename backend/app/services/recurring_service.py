from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.models.recurring import RecurringExpense
from app.models.expense import Expense

class RecurringService:
    def process_due_recurring_expenses(self, db: Session) -> int:
        now = datetime.utcnow()
        due_items = db.query(RecurringExpense).filter(
            RecurringExpense.is_active == True,
            RecurringExpense.next_due_date <= now
        ).all()

        count = 0
        for item in due_items:
            # Auto-create actual expense record
            expense = Expense(
                user_id=item.user_id,
                category_id=item.category_id,
                amount=item.amount,
                description=f"[Recurring] {item.description}",
                date=item.next_due_date,
                payment_mode="Auto-Debit",
                raw_telegram_text=f"Auto-generated recurring: {item.description}"
            )
            db.add(expense)

            # Update next due date
            item.last_processed_at = now
            if item.frequency == "daily":
                item.next_due_date = item.next_due_date + timedelta(days=1)
            elif item.frequency == "weekly":
                item.next_due_date = item.next_due_date + timedelta(weeks=1)
            elif item.frequency == "monthly":
                # Add 30 days
                item.next_due_date = item.next_due_date + timedelta(days=30)
            elif item.frequency == "yearly":
                item.next_due_date = item.next_due_date + timedelta(days=365)

            count += 1

        db.commit()
        return count

recurring_service = RecurringService()
