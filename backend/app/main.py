import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.router import api_router
from app.bot.telegram_bot import build_telegram_application

logger = logging.getLogger(__name__)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

telegram_app = build_telegram_application()
telegram_task: asyncio.Task | None = None

@app.on_event("startup")
async def startup_event():
    global telegram_task
    if telegram_app is not None:
        logger.info("Starting Telegram bot polling...")
        await telegram_app.initialize()
        telegram_task = asyncio.create_task(asyncio.to_thread(telegram_app.run_polling))

@app.on_event("shutdown")
async def shutdown_event():
    global telegram_task
    if telegram_app is not None:
        logger.info("Stopping Telegram bot...")
        if telegram_task is not None:
            telegram_task.cancel()
            telegram_task = None
        await telegram_app.shutdown()

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
