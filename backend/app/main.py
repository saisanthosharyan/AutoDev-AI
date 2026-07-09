from fastapi import FastAPI
from app.database.database import Base, engine
from app.database import models

from app.api.chat import router as chat_router
from app.core.config import settings
from app.services.llm.router import LLMRouter
from app.api.download import router as download_router
from app.api.projects import router as projects_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Autonomous AI Software Engineer API",
)
Base.metadata.create_all(bind=engine)
app.include_router(chat_router)
app.include_router(download_router)
app.include_router(projects_router)

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