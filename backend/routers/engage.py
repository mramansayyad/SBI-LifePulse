import logging
from fastapi import APIRouter, Request, HTTPException
from backend.models.engagement import EngagementPlan
from typing import List, Dict, Any

router = APIRouter(prefix="/engage", tags=["engage"])
logger = logging.getLogger("lifepulse.routers.engage")

@router.get("/feed", response_model=List[Dict[str, Any]])
async def get_realtime_engagement_feed(request: Request):
    """
    Get the scrolling real-time engagement activity feed logs.
    """
    try:
        firestore_service = request.app.state.firestore_service
        feed = await firestore_service.get_engagement_feed()
        return feed
    except Exception as e:
        logger.error(f"Error fetching engagement feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}", response_model=EngagementPlan)
async def get_engagement_plan_endpoint(customer_id: str, request: Request):
    """
    Get or automatically generate an engagement plan for a customer.
    """
    firestore_service = request.app.state.firestore_service
    engagement_agent = request.app.state.engagement_agent
    
    plan = await firestore_service.get_engagement_plan(customer_id)
    if plan:
        return plan
        
    # If plan doesn't exist, we try to generate it on the fly
    customer = await firestore_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    event = await firestore_service.get_life_event(customer_id)
    if not event:
        # If no life event detected yet, run detection first
        life_event_agent = request.app.state.life_event_agent
        try:
            event = await life_event_agent.detect_life_event(customer_id)
        except Exception as e:
            logger.error(f"Failed to auto-detect event for {customer_id}: {e}")
            raise HTTPException(status_code=400, detail="Cannot generate engagement plan: No life event detected and detection failed.")

    try:
        plan = await engagement_agent.generate_engagement_plan(customer, event)
        return plan
    except Exception as e:
        logger.error(f"Failed to generate engagement plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{customer_id}/trigger", response_model=Dict[str, Any])
async def trigger_customer_outreach(customer_id: str, request: Request):
    """
    Trigger engagement outreach simulation (logs to activity feed and updates status).
    """
    firestore_service = request.app.state.firestore_service
    
    customer = await firestore_service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    plan = await firestore_service.get_engagement_plan(customer_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No engagement plan found. Generate one first.")
        
    # Update customer engagement status
    customer.engagement_status = "engaged"
    await firestore_service.save_customer(customer)
    
    # Log to real-time activity feed
    activity_msg = f"Outreach triggered via WhatsApp to {customer.name} for {plan.life_event} recommendations."
    await firestore_service.log_engagement_activity({
        "customer_id": customer_id,
        "customer_name": customer.name,
        "event_type": f"OUTREACH_{plan.life_event}",
        "message": activity_msg,
        "urgency": "HIGH" if customer.detected_life_event in ["MARRIAGE", "JOB_CHANGE", "NEW_BABY", "HOME_PURCHASE"] else "MEDIUM"
    })
    
    return {
        "status": "success",
        "customer_id": customer_id,
        "engagement_status": "engaged",
        "message": f"Engagement message simulated successfully via WhatsApp: '{plan.opening_message[:40]}...'"
    }
