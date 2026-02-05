from fastapi import FastAPI
from app.api.routes import router
import os
import uvicorn

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
