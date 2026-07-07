from app.services.llm.router import LLMRouter
from app.core.config import settings
from fastapi import FastAPI
from app.api.chat import router as chat_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Autonomous AI Software Engineer API",
)

# Register the chat API
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
def current_llm():
    llm = LLMRouter.get_llm()

    return {
        "provider": settings.LLM_PROVIDER,
        "service": llm.__class__.__name__,
    }