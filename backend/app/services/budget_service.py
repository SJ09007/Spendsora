from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.budget import Budget
from app.models.expense import Expense
from app.models.notification import Notification

class BudgetService:
    def get_user_budgets_with_spending(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        result = []
        for b in budgets:
            spent = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                Expense.category_id == b.category_id,
                Expense.date >= month_start
            ).scalar()

            spent_val = float(spent)
            limit_val = float(b.amount_limit)
            percentage = round((spent_val / limit_val) * 100, 1) if limit_val > 0 else 0.0

            result.append({
                "id": b.id,
                "user_id": b.user_id,
                "category_id": b.category_id,
                "category": b.category,
                "amount_limit": limit_val,
                "spent": spent_val,
                "percentage": percentage,
                "period": b.period,
                "alert_80_sent": b.alert_80_sent,
                "alert_90_sent": b.alert_90_sent,
                "alert_100_sent": b.alert_100_sent,
                "start_date": b.start_date,
                "created_at": b.created_at
            })

        return result

    def check_and_trigger_budget_alerts(self, db: Session, user_id: int, category_id: int) -> Optional[str]:
        budget = db.query(Budget).filter(Budget.user_id == user_id, Budget.category_id == category_id).first()
        if not budget:
            return None

        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        spent = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == user_id,
            Expense.category_id == category_id,
            Expense.date >= month_start
        ).scalar())

        limit_val = float(budget.amount_limit)
        if limit_val <= 0:
            return None

        percentage = (spent / limit_val) * 100
        cat_name = budget.category.name if budget.category else "Category"
        alert_msg = None

        if percentage >= 100 and not budget.alert_100_sent:
            budget.alert_100_sent = True
            alert_msg = f"🚨 Alert: You have reached 100% of your {cat_name} budget! (Spent: ₹{spent:.2f} / Limit: ₹{limit_val:.2f})"
        elif percentage >= 90 and not budget.alert_90_sent:
            budget.alert_90_sent = True
            alert_msg = f"⚠️ Warning: You have reached 90% of your {cat_name} budget! (Spent: ₹{spent:.2f} / Limit: ₹{limit_val:.2f})"
        elif percentage >= 80 and not budget.alert_80_sent:
            budget.alert_80_sent = True
            alert_msg = f"⚡ Alert: You have reached 80% of your {cat_name} budget! (Spent: ₹{spent:.2f} / Limit: ₹{limit_val:.2f})"

        if alert_msg:
            # Create in-app Notification record
            notif = Notification(
                user_id=user_id,
                title=f"Budget Alert: {cat_name}",
                message=alert_msg,
                type="budget_alert"
            )
            db.add(notif)
            db.commit()

        return alert_msg

budget_service = BudgetService()
