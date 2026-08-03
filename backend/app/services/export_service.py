import io
import csv
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.expense import Expense

class ExportService:
    def export_to_csv(self, db: Session, user_id: int) -> str:
        expenses = db.query(Expense).filter(Expense.user_id == user_id).order_by(Expense.date.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["ID", "Date", "Description", "Category", "Merchant", "Amount (₹)", "Payment Mode", "Raw Telegram Text"])
        
        for exp in expenses:
            cat_name = exp.category.name if exp.category else "Uncategorized"
            writer.writerow([
                exp.id,
                exp.date.strftime("%Y-%m-%d %H:%M"),
                exp.description,
                cat_name,
                exp.merchant or "",
                float(exp.amount),
                exp.payment_mode,
                exp.raw_telegram_text or ""
            ])
            
        return output.getvalue()

export_service = ExportService()
