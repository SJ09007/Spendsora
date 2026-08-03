from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from app.models.expense import Expense
from app.models.category import Category
from app.models.ai_insight import AIInsight

class AIInsightService:
    def generate_insights(self, db: Session, user_id: int) -> List[AIInsight]:
        now = datetime.utcnow()
        current_month_start = datetime(now.year, now.month, 1)

        # Previous month
        if now.month == 1:
            prev_month_start = datetime(now.year - 1, 12, 1)
        else:
            prev_month_start = datetime(now.year, now.month - 1, 1)

        insights = []

        # 1. Compare current month spending vs previous month per category
        categories = db.query(Category).all()
        for cat in categories:
            curr_spent = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                Expense.category_id == cat.id,
                Expense.date >= current_month_start
            ).scalar())

            prev_spent = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                Expense.category_id == cat.id,
                Expense.date >= prev_month_start,
                Expense.date < current_month_start
            ).scalar())

            if prev_spent > 0 and curr_spent > 0:
                diff_pct = ((curr_spent - prev_spent) / prev_spent) * 100
                if diff_pct >= 20:
                    content = f"You spent {diff_pct:.0f}% more on {cat.name} this month compared to last month."
                    insights.append(self._create_or_get_insight(db, user_id, "category_spike", content))
                elif diff_pct <= -20:
                    content = f"Great job! Your {cat.name} spending decreased by {abs(diff_pct):.0f}% this month."
                    insights.append(self._create_or_get_insight(db, user_id, "saving_suggestion", content))

        # 2. Daily Average Insight
        first_exp = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.date.asc()).first()
        if first_exp:
            days_active = max((now - first_exp.date).days + 1, 1)
            total_spent = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user_id).scalar())
            avg_daily = total_spent / days_active
            content = f"Your average daily spending is ₹{avg_daily:.0f}."
            insights.append(self._create_or_get_insight(db, user_id, "trend", content))

        # Return all active insights
        return db.query(AIInsight).filter(AIInsight.user_id == user_id, AIInsight.is_dismissed == False).order_by(desc(AIInsight.created_at)).all()

    def _create_or_get_insight(self, db: Session, user_id: int, insight_type: str, content: str) -> AIInsight:
        existing = db.query(AIInsight).filter(
            AIInsight.user_id == user_id,
            AIInsight.insight_type == insight_type,
            AIInsight.content == content
        ).first()

        if existing:
            return existing

        new_insight = AIInsight(
            user_id=user_id,
            period="monthly",
            insight_type=insight_type,
            content=content
        )
        db.add(new_insight)
        db.commit()
        db.refresh(new_insight)
        return new_insight

ai_insight_service = AIInsightService()
