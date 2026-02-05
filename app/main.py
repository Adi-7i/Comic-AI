"""
Main FastAPI application.

Entry point for the Comic Generation SaaS backend.
Includes authentication, authorization, and plan enforcement.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import init_db
from app.api.v1.routes import auth, projects, scenes, story, generation, delivery



# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered comic generation SaaS backend with authentication and plan enforcement",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup.
    
    Connects to MongoDB and initializes Beanie with all models.
    Creates indexes automatically.
    """
    await init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown.
    """
    print(f"👋 {settings.APP_NAME} shutting down")


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(scenes.router, prefix="/api/v1")
app.include_router(story.router, prefix="/api/v1")
app.include_router(generation.router, prefix="/api/v1")
app.include_router(delivery.router, prefix="/api/v1/projects", tags=["PDF Delivery"])  # Step-7


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m app.main
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
