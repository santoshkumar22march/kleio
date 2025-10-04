# Chat/Telegram webhook endpoint for LangChain agent

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from database import get_db
from utils.auth import get_current_user
from agent.langchain_agent import process_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat Agent"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I bought 2kg tomatoes and 1 liter milk",
                "thread_id": "telegram-user123"
            }
        }


class ChatResponse(BaseModel):
    response: str
    thread_id: str


@router.post(
    "/message",
    response_model=ChatResponse,
    summary="Send message to AI assistant",
    description="Converse with Kleio AI assistant for inventory management"
)
async def send_message(
    request: ChatRequest,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send message to AI assistant and get response.
    
    The agent can:
    - Add items to inventory ("bought 2kg tomatoes")
    - Generate shopping lists ("what should I buy?")
    - Suggest recipes ("suggest a recipe")
    - Check inventory ("what do I have?")
    
    Maintains conversation context using thread_id.
    """
    
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    logger.info(f"Chat message from {firebase_uid}: {request.message}")
    
    try:
        # Process message through LangChain agent
        response = await process_message(
            firebase_uid=firebase_uid,
            message=request.message,
            thread_id=request.thread_id
        )
        
        return ChatResponse(
            response=response,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


# Telegram Webhook endpoint example
class TelegramUpdate(BaseModel):
    message: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": {
                    "from": {"id": 123456789, "first_name": "John"},
                    "chat": {"id": 123456789},
                    "text": "I bought tomatoes and milk"
                }
            }
        }


@router.post(
    "/webhook/telegram",
    summary="Telegram bot webhook",
    description="Receive messages from Telegram bot"
)
async def telegram_webhook(
    update: TelegramUpdate,
    db: Session = Depends(get_db)
):
    """
    Telegram bot webhook endpoint.
    
    Flow:
    1. Telegram user sends message
    2. Telegram forwards to this webhook
    3. LangChain agent processes message
    4. Response sent back to Telegram user
    
    Note: You need to map Telegram user ID to Firebase UID.
    For now, this is a placeholder showing the integration pattern.
    """
    
    try:
        telegram_user_id = update.message.get("from", {}).get("id")
        message_text = update.message.get("text", "")
        
        if not telegram_user_id or not message_text:
            return {"status": "error", "message": "Invalid update format"}
        
        # TODO: Map telegram_user_id to firebase_uid
        # For now, using telegram_user_id as thread_id
        # In production, you'd have a mapping table
        firebase_uid = "demo_user"  # Replace with actual mapping
        thread_id = f"telegram-{telegram_user_id}"
        
        logger.info(f"Telegram message from {telegram_user_id}: {message_text}")
        
        # Process through agent (use async version in async endpoint)
        response = await process_message(
            firebase_uid=firebase_uid,
            message=message_text,
            thread_id=thread_id
        )
        
        # TODO: Send response back to Telegram
        # You'll need to use Telegram Bot API to send the response
        # Example: telegram_bot.send_message(chat_id=telegram_user_id, text=response)
        
        return {
            "status": "success",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return {"status": "error", "message": str(e)}

