from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_limit = Column(Numeric(12, 2), nullable=False)
    period = Column(String(20), default="monthly")  # monthly, weekly, yearly
    start_date = Column(DateTime, default=datetime.utcnow)
    alert_80_sent = Column(Boolean, default=False)
    alert_90_sent = Column(Boolean, default=False)
    alert_100_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
