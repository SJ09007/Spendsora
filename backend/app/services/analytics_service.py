from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from app.models.expense import Expense
from app.models.category import Category

class AnalyticsService:
    def get_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = datetime(now.year, now.month, 1)
        year_start = datetime(now.year, 1, 1)

        # Base query
        query = db.query(Expense).filter(Expense.user_id == user_id)
        total_spending = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user_id).scalar())
        today_spending = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user_id, Expense.date >= today_start).scalar())
        weekly_spending = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user_id, Expense.date >= week_start).scalar())
        monthly_spending = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user_id, Expense.date >= month_start).scalar())
        yearly_spending = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(Expense.user_id == user_id, Expense.date >= year_start).scalar())

        total_count = db.query(Expense).filter(Expense.user_id == user_id).count()
        
        # Days active calculation
        first_expense = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.date.asc()).first()
        days_active = (now - first_expense.date).days + 1 if first_expense else 1
        avg_per_day = round(total_spending / max(days_active, 1), 2)
        avg_per_transaction = round(total_spending / max(total_count, 1), 2)

        # Highest & Lowest
        highest = db.query(Expense).filter(Expense.user_id == user_id).order_by(desc(Expense.amount)).first()
        lowest = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.amount.asc()).first()

        # Top Category
        top_cat_result = (
            db.query(Category.name, func.sum(Expense.amount).label("total"))
            .join(Expense, Expense.category_id == Category.id)
            .filter(Expense.user_id == user_id)
            .group_by(Category.name)
            .order_by(desc("total"))
            .first()
        )
        top_category = top_cat_result[0] if top_cat_result else "N/A"

        return {
            "total_spending": round(total_spending, 2),
            "today_spending": round(today_spending, 2),
            "weekly_spending": round(weekly_spending, 2),
            "monthly_spending": round(monthly_spending, 2),
            "yearly_spending": round(yearly_spending, 2),
            "avg_per_day": avg_per_day,
            "avg_per_transaction": avg_per_transaction,
            "highest_expense": {"amount": float(highest.amount), "description": highest.description} if highest else None,
            "lowest_expense": {"amount": float(lowest.amount), "description": lowest.description} if lowest else None,
            "top_category": top_category,
            "total_transactions": total_count
        }

    def get_charts_data(self, db: Session, user_id: int) -> Dict[str, Any]:
        # 1. Category-wise pie chart
        cat_query = (
            db.query(
                Category.id,
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Expense.amount).label("total_amount"),
                func.count(Expense.id).label("count")
            )
            .join(Expense, Expense.category_id == Category.id)
            .filter(Expense.user_id == user_id)
            .group_by(Category.id, Category.name, Category.icon, Category.color)
            .all()
        )

        grand_total = sum([float(item.total_amount) for item in cat_query]) or 1.0

        categories = [
            {
                "category_id": item.id,
                "category_name": item.name,
                "icon": item.icon,
                "color": item.color,
                "total_amount": round(float(item.total_amount), 2),
                "percentage": round((float(item.total_amount) / grand_total) * 100, 1),
                "count": item.count
            }
            for item in cat_query
        ]

        # 2. Daily spending line chart (Last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_query = (
            db.query(
                func.date(Expense.date).label("exp_date"),
                func.sum(Expense.amount).label("total")
            )
            .filter(Expense.user_id == user_id, Expense.date >= thirty_days_ago)
            .group_by(func.date(Expense.date))
            .order_by("exp_date")
            .all()
        )

        daily_trend = [
            {"date": str(item.exp_date), "amount": round(float(item.total), 2)}
            for item in daily_query
        ]

        # 3. Top Merchants
        merchant_query = (
            db.query(
                Expense.merchant,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count")
            )
            .filter(Expense.user_id == user_id, Expense.merchant.isnot(None))
            .group_by(Expense.merchant)
            .order_by(desc("total"))
            .limit(5)
            .all()
        )

        top_merchants = [
            {"merchant": item.merchant, "amount": round(float(item.total), 2), "count": item.count}
            for item in merchant_query
        ]

        # 4. Payment Modes
        pm_query = (
            db.query(
                Expense.payment_mode,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count")
            )
            .filter(Expense.user_id == user_id)
            .group_by(Expense.payment_mode)
            .all()
        )

        payment_modes = [
            {"mode": item.payment_mode, "amount": round(float(item.total), 2), "count": item.count}
            for item in pm_query
        ]

        return {
            "categories": categories,
            "daily_trend": daily_trend,
            "top_merchants": top_merchants,
            "payment_modes": payment_modes
        }

analytics_service = AnalyticsService()
