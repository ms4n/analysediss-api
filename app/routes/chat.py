from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chat_service import ChatService
import logging

router = APIRouter()
chat_service = ChatService()


class ChatMessage(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        response = await chat_service.process_message(chat_message.session_id, chat_message.message)
        return {"response": response}
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/chat_history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        history = chat_service.get_chat_history(session_id)
        return {"chat_history": history}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
