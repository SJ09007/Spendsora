from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    telegram_alerts_enabled = Column(Boolean, default=True)
    daily_summary_time = Column(String(10), default="21:00")  # 24h format HH:MM
    weekly_report_day = Column(String(10), default="Sunday")
    monthly_report_day = Column(Integer, default=1)
    preferred_currency = Column(String(10), default="₹")
    dark_mode_default = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")
