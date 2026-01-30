from fastapi import FastAPI
from app.api import routes
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservice to convert docs to LLM-ready Markdown using Docling.",
    version="1.0.0"
)

# Include Routers
app.include_router(routes.router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "docling-converter"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)