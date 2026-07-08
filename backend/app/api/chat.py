from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.orchestrator import AgentOrchestrator
from app.memory.conversation import (
    add_message,
    get_history,
)

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):

    try:

        history = get_history(request.session_id)

        add_message(
            request.session_id,
            "user",
            request.message,
        )

        orchestrator = AgentOrchestrator()

        result = await orchestrator.execute(
            request.message,
            history,
        )

        add_message(
            request.session_id,
            "assistant",
            result["review"],
        )

        return {
            "session_id": request.session_id,
            "history": get_history(request.session_id),
            "plan": result["plan"],
            "code": result["code"],
            "review": result["review"],
            "improved_code": result["improved_code"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )