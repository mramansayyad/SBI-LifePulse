import logging
from fastapi import APIRouter, Request, HTTPException
from backend.models.customer import CustomerProfile
from typing import List, Dict, Any

router = APIRouter(prefix="/customers", tags=["customers"])
logger = logging.getLogger("lifepulse.routers.customers")

@router.get("", response_model=List[Dict[str, Any]])
async def list_customers(request: Request):
    """
    List all customers in the system along with their detected life events.
    """
    try:
        firestore_service = request.app.state.firestore_service
        customers = await firestore_service.get_all_customers_with_events()
        # Strip large transaction records for list view performance
        for c in customers:
            if "transactions" in c:
                c["transactions_count"] = len(c["transactions"])
                c["transactions"] = [] # Return empty list in index to save payload
        return customers
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}", response_model=CustomerProfile)
async def get_customer_profile(customer_id: str, request: Request):
    """
    Retrieve full customer 360-degree profile.
    """
    firestore_service = request.app.state.firestore_service
    customer = await firestore_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/{customer_id}/transactions", response_model=Dict[str, Any])
async def get_customer_transactions(customer_id: str, request: Request):
    """
    Get customer transactions and highlight analyzed signals.
    """
    firestore_service = request.app.state.firestore_service
    bq_service = request.app.state.bq_service
    
    customer = await firestore_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    transactions_dict = [t.model_dump() for t in customer.transactions]
    signals = bq_service.extract_behavioral_signals(transactions_dict)
    
    return {
        "customer_id": customer_id,
        "transactions": customer.transactions,
        "extracted_signals": signals["signals"],
        "raw_stats": signals["raw_stats"]
    }

@router.post("/{customer_id}/analyze", response_model=Dict[str, Any])
async def analyze_customer_events(customer_id: str, request: Request):
    """
    Manually trigger life event detection for a specific customer.
    """
    life_event_agent = request.app.state.life_event_agent
    try:
        result = await life_event_agent.detect_life_event(customer_id)
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error during manual customer event analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
