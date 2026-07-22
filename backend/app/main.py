from fastapi import FastAPI

from app.core.config import settings

from app.database.database import Base, engine
from app.database import models

from app.services.llm.router import LLMRouter

from app.api.chat import router as chat_router
from app.api.download import router as download_router
from app.api.projects import router as projects_router
from app.api.ws import router as ws_router
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------------------------------
# FastAPI Application
# -------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Autonomous AI Software Engineer API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Database
# -------------------------------------------------------

Base.metadata.create_all(bind=engine)


# -------------------------------------------------------
# API Routes
# -------------------------------------------------------

app.include_router(chat_router)
app.include_router(download_router)
app.include_router(projects_router)
app.include_router(ws_router)


# -------------------------------------------------------
# Root
# -------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} 🚀"
    }


# -------------------------------------------------------
# Health Check
# -------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
    }


# -------------------------------------------------------
# Current LLM
# -------------------------------------------------------

@app.get("/llm")
async def current_llm():
    llm = LLMRouter.get_llm()

    return {
        "provider": settings.LLM_PROVIDER,
        "service": llm.__class__.__name__,
    }