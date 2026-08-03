import re
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, or_, desc
from app.models.expense import Expense
from app.models.category import Category

class SearchService:
    def execute_natural_search(self, db: Session, user_id: int, query_text: str) -> Dict[str, Any]:
        text = query_text.lower().strip()
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        # Query Type 1: Biggest Expense ("What was my biggest expense?", "highest expense")
        if "biggest" in text or "highest" in text or "maximum" in text or "max" in text:
            expense = db.query(Expense).filter(Expense.user_id == user_id).order_by(desc(Expense.amount)).first()
            if expense:
                return {
                    "type": "single_expense",
                    "answer": f"Your biggest expense was ₹{float(expense.amount):.2f} for '{expense.description}' on {expense.date.strftime('%b %d, %Y')}.",
                    "data": [expense]
                }
            return {"type": "info", "answer": "No expenses found yet.", "data": []}

        # Query Type 2: Lowest Expense
        if "lowest" in text or "smallest" in text or "minimum" in text or "min" in text:
            expense = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.amount.asc()).first()
            if expense:
                return {
                    "type": "single_expense",
                    "answer": f"Your lowest expense was ₹{float(expense.amount):.2f} for '{expense.description}'.",
                    "data": [expense]
                }
            return {"type": "info", "answer": "No expenses found.", "data": []}

        # Query Type 3: Threshold Filter ("Show expenses above 1000", "expenses greater than 500")
        above_match = re.search(r'(?:above|greater than|more than|>|\+)\s*(?:₹|rs\.?)?\s*(\d+)', text)
        if above_match:
            min_amt = float(above_match.group(1))
            expenses = db.query(Expense).filter(Expense.user_id == user_id, Expense.amount >= min_amt).order_by(desc(Expense.date)).all()
            total = sum([float(e.amount) for e in expenses])
            return {
                "type": "list",
                "answer": f"Found {len(expenses)} expenses above ₹{min_amt:.0f} totaling ₹{total:.2f}.",
                "data": expenses
            }

        # Query Type 4: Vendor / Merchant specific search ("How much did I spend on Amazon?")
        known_merchants = ["amazon", "flipkart", "swiggy", "zomato", "uber", "ola", "netflix", "starbucks"]
        matched_merchant = None
        for m in known_merchants:
            if m in text:
                matched_merchant = m
                break

        if matched_merchant:
            expenses = db.query(Expense).filter(
                Expense.user_id == user_id,
                or_(
                    Expense.merchant.ilike(f"%{matched_merchant}%"),
                    Expense.description.ilike(f"%{matched_merchant}%")
                )
            ).order_by(desc(Expense.date)).all()
            total = sum([float(e.amount) for e in expenses])
            return {
                "type": "aggregate",
                "answer": f"You have spent a total of ₹{total:.2f} across {len(expenses)} transactions on {matched_merchant.capitalize()}.",
                "data": expenses
            }

        # Query Type 5: Category Specific ("How much did I spend on food this month?")
        categories = db.query(Category).all()
        matched_category = None
        for cat in categories:
            if cat.name.lower() in text:
                matched_category = cat
                break

        if matched_category:
            expenses = db.query(Expense).filter(
                Expense.user_id == user_id,
                Expense.category_id == matched_category.id,
                Expense.date >= month_start
            ).order_by(desc(Expense.date)).all()
            total = sum([float(e.amount) for e in expenses])
            return {
                "type": "aggregate",
                "answer": f"You spent ₹{total:.2f} on {matched_category.name} this month across {len(expenses)} transactions.",
                "data": expenses
            }

        # General Fallback Keyword Search
        expenses = db.query(Expense).filter(
            Expense.user_id == user_id,
            or_(
                Expense.description.ilike(f"%{text}%"),
                Expense.raw_telegram_text.ilike(f"%{text}%")
            )
        ).order_by(desc(Expense.date)).all()

        total = sum([float(e.amount) for e in expenses])
        return {
            "type": "list",
            "answer": f"Found {len(expenses)} matching expenses totaling ₹{total:.2f}.",
            "data": expenses
        }

search_service = SearchService()
