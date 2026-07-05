from fastapi import FastAPI
from app.core.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Autonomous AI Software Engineer API",
)

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