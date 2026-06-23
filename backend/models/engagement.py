from datetime import datetime
from typing import List
from pydantic import BaseModel

class ProductRecommendation(BaseModel):
    product_name: str
    product_id: str
    why_now: str
    expected_benefit: str
    cta_text: str

class EngagementPlan(BaseModel):
    customer_id: str
    life_event: str
    opening_message: str
    conversation_starters: List[str]
    product_recommendations: List[ProductRecommendation]
    channel_priority: List[str]
    best_contact_time: str
    created_at: datetime
