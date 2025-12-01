from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.backend.core.settings import get_settings
from app.backend.api.v1.chat import router as chat_router

settings = get_settings()

def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(chat_router, prefix=settings.API_V1_STR, tags=["Chat"])

    return application

app = get_application()

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"message": "application is up and running."}

if __name__ == "__main__":
    import uvicorn
    # For dubugging purposes.
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=8000, reload=True)