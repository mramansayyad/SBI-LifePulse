from datetime import datetime
from typing import Literal, List
from pydantic import BaseModel, Field

class LifeEventDetection(BaseModel):
    customer_id: str
    detected_event: Literal[
        "MARRIAGE", "JOB_CHANGE", "NEW_BABY", "HOME_PURCHASE", 
        "PRE_RETIREMENT", "SALARY_HIKE", "TRAVEL_PHASE", "NONE"
    ]
    confidence_score: float = Field(ge=0.0, le=1.0)
    key_signals: List[str]
    recommended_products: List[str]
    engagement_urgency: Literal["HIGH", "MEDIUM", "LOW"]
    personalized_hook: str
    detected_at: datetime
