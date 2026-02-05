"""
Database initialization module.

Handles MongoDB connection and Beanie ODM initialization.
"""

import os
import ssl
from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.user import User
from app.models.project import Project
from app.models.character import Character
from app.models.scene import Scene
from app.models.generation import Generation
from app.models.payment import Payment
from app.models.audit_log import AuditLog
from app.models.comic_asset import ComicAsset  # Step-6: Image Generation


from app.core.config import settings

# MongoDB connection string from environment settings
MONGODB_URL = settings.MONGODB_URL
DATABASE_NAME = settings.DATABASE_NAME


async def init_db() -> AsyncIOMotorClient:
    """
    Initialize database connection and Beanie ODM.
    
    This function should be called on application startup.
    It establishes the MongoDB connection and initializes Beanie
    with all document models, creating indexes automatically.
    
    Returns:
        AsyncIOMotorClient: MongoDB client instance
        
    Example:
        # In FastAPI app startup
        @app.on_event("startup")
        async def startup_event():
            await init_db()
    """
    # Create Motor async client with SSL certificate bypass for development
    # For production, use proper certificate validation
    client = AsyncIOMotorClient(
        MONGODB_URL,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
    )
    
    # Get database
    database = client[DATABASE_NAME]
    
    # Initialize Beanie with all document models
    await init_beanie(
        database=database,
        document_models=[
            User,
            Project,
            Character,
            Scene,
            Generation,
            Payment,
            AuditLog,
            ComicAsset,  # Step-6: Image Generation
        ],
    )
    
    print(f"✅ Database initialized: {DATABASE_NAME}")
    print(f"📊 Collections: users, projects, characters, scenes, generations, payments, audit_logs, comic_assets")
    
    return client


async def close_db(client: AsyncIOMotorClient) -> None:
    """
    Close database connection.
    
    Should be called on application shutdown.
    
    Args:
        client: MongoDB client instance to close
        
    Example:
        # In FastAPI app shutdown
        @app.on_event("shutdown")
        async def shutdown_event():
            await close_db(app.state.db_client)
    """
    client.close()
    print("✅ Database connection closed")


async def health_check() -> bool:
    """
    Check database health.
    
    Returns:
        bool: True if database is reachable, False otherwise
        
    Example:
        # In health endpoint
        @app.get("/health")
        async def health():
            db_healthy = await health_check()
            return {"status": "healthy" if db_healthy else "unhealthy"}
    """
    try:
        client = AsyncIOMotorClient(
            MONGODB_URL,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        await client.admin.command('ping')
        client.close()
        return True
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False
