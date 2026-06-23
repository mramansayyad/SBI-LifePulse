import logging
from fastapi import APIRouter, Request, HTTPException
from backend.models.life_event import LifeEventDetection
from typing import List, Dict, Any

router = APIRouter(prefix="/events", tags=["events"])
logger = logging.getLogger("lifepulse.routers.events")

@router.get("", response_model=List[LifeEventDetection])
async def list_all_detected_events(request: Request):
    """
    Get all detected life events across all customers.
    """
    try:
        firestore_service = request.app.state.firestore_service
        customers = await firestore_service.get_all_customers_with_events()
        events = []
        for c in customers:
            if "life_event_details" in c:
                events.append(LifeEventDetection.model_validate(c["life_event_details"]))
        return events
    except Exception as e:
        logger.error(f"Error fetching detected events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}", response_model=LifeEventDetection)
async def get_customer_event(customer_id: str, request: Request):
    """
    Get a specific customer's detected life event.
    """
    firestore_service = request.app.state.firestore_service
    event = await firestore_service.get_life_event(customer_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"No detected event found for customer {customer_id}")
    return event

@router.post("/detect-all", response_model=Dict[str, Any])
async def detect_all_life_events(request: Request):
    """
    Triggers event detection for all customers in the system (Global demo trigger).
    """
    firestore_service = request.app.state.firestore_service
    life_event_agent = request.app.state.life_event_agent
    
    try:
        customers = await firestore_service.get_all_customers_with_events()
        detected_count = 0
        details = []
        
        for c in customers:
            customer_id = c["customer_id"]
            try:
                res = await life_event_agent.detect_life_event(customer_id)
                detected_count += 1
                details.append({
                    "customer_id": customer_id,
                    "customer_name": c["name"],
                    "detected_event": res.detected_event,
                    "confidence": res.confidence_score
                })
            except Exception as ex:
                logger.error(f"Failed analysis for customer {customer_id}: {ex}")
                
        return {
            "status": "success",
            "message": f"Successfully analyzed {len(customers)} customers.",
            "detected_count": detected_count,
            "details": details
        }
    except Exception as e:
        logger.error(f"Error during global event detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
