import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger("lifepulse.routers.chat")

class ChatRequest(BaseModel):
    message: str

@router.post("/{customer_id}", response_model=Dict[str, Any])
async def chat_with_arya(customer_id: str, payload: ChatRequest, request: Request):
    """
    Send a message to conversational financial companion Arya.
    """
    conversation_agent = request.app.state.conversation_agent
    try:
        response = await conversation_agent.respond(customer_id, payload.message)
        return {
            "customer_id": customer_id,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error chatting with Arya: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}/history", response_model=List[Dict[str, Any]])
async def get_chat_history(customer_id: str, request: Request):
    """
    Get full stateful conversation turns for a customer.
    """
    conversation_agent = request.app.state.conversation_agent
    try:
        history = await conversation_agent.get_history(customer_id)
        return history
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{customer_id}", response_model=Dict[str, Any])
async def reset_chat_session(customer_id: str, request: Request):
    """
    Reset conversation turns for a customer.
    """
    conversation_agent = request.app.state.conversation_agent
    try:
        await conversation_agent.reset(customer_id)
        return {
            "status": "success",
            "message": f"Conversation session for customer {customer_id} reset successfully."
        }
    except Exception as e:
        logger.error(f"Error resetting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
