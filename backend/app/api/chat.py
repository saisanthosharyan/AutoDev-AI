from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm.router import LLMRouter

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    llm = LLMRouter.get_llm()

    response = await llm.generate(request.message)

    return {
        "response": response
    }