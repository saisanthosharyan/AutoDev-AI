from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.orchestrator import AgentOrchestrator
from app.memory.conversation_cache import (
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
        # Get previous conversation history
        history = get_history(request.session_id)

        # Save user message
        add_message(
            request.session_id,
            "user",
            request.message,
        )

        orchestrator = AgentOrchestrator()

        result = await orchestrator.execute(
            task=request.message,
            history=history,
            session_id=request.session_id,
        )

        # Save assistant response
        add_message(
            request.session_id,
            "assistant",
            result.get("review", ""),
        )

        project = result.get("project", {})

        download_url = None
        if (
            isinstance(project, dict)
            and project.get("project_path")
        ):
            download_url = (
                f"/download/{Path(project['project_path']).name}"
            )

        return {
            "session_id": request.session_id,
            "history": get_history(request.session_id),
            "plan": result.get("plan"),
            "project": {
                **project,
                "download_url": download_url,
            },
            "execution": result.get("execution"),
            "validation": result.get("validation"),
            "tests": result.get("tests"),
            "debug_report": result.get("debug_report"),
            "review": result.get("review"),
            "improved_code": result.get("improved_code"),
        }

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )