from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, models, system

app = FastAPI(title="AI Local Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(system.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
