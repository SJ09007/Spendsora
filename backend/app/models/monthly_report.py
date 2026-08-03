from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    month_year = Column(String(7), nullable=False, index=True)  # YYYY-MM
    total_spending = Column(Numeric(12, 2), default=0.00)
    total_income = Column(Numeric(12, 2), default=0.00)
    net_savings = Column(Numeric(12, 2), default=0.00)
    report_json = Column(Text, nullable=True)  # JSON summary dump
    pdf_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="monthly_reports")
