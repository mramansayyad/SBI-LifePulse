from datetime import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel

class Transaction(BaseModel):
    transaction_id: str
    date: datetime
    amount: float
    merchant_category: str
    merchant_name: str
    transaction_type: Literal["debit", "credit"]
    channel: Literal["UPI", "NEFT", "RTGS", "ATM", "card", "net_banking"]
    description: str

class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    age: int
    city: str
    account_number: str
    monthly_income: float
    risk_profile: Literal["conservative", "moderate", "aggressive"]
    existing_products: List[str]
    transactions: List[Transaction] = []
    detected_life_event: Optional[str] = None
    engagement_status: Literal["pending", "engaged", "converted", "churned"] = "pending"
