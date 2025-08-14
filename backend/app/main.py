from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config.settings import settings
from app.routers import resume

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(resume.router, prefix=settings.API_V1_STR)
    
    @app.get("/")
    def read_root():
        return {
            "message": "Resume Parser API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    return app

app = create_app()
