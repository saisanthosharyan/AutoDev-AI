from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.core.config import settings
from app.services.llm.router import LLMRouter

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Autonomous AI Software Engineer API",
)

app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} 🚀"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/llm")
async def current_llm():
    llm = LLMRouter.get_llm()

    return {
        "provider": settings.LLM_PROVIDER,
        "service": llm.__class__.__name__,
    }