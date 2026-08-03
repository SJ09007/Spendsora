from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class AIInsightResponse(BaseModel):
    id: int
    user_id: int
    period: str
    insight_type: str
    content: str
    metrics_json: Optional[str] = None
    is_dismissed: bool
    created_at: datetime

    class Config:
        from_attributes = True
