from app.core.config import settings

print("Gemini Key:", settings.GEMINI_API_KEY[:10] + "...")
print("Model:", settings.GEMINI_MODEL)