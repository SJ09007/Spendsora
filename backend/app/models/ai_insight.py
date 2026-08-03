from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String(20), default="monthly")  # weekly, monthly
    insight_type = Column(String(50), nullable=False)  # unusual_spending, trend, saving_suggestion, category_spike
    content = Column(Text, nullable=False)
    metrics_json = Column(Text, nullable=True)  # Additional metric details
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ai_insights")
