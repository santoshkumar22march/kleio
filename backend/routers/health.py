# Health check endpoints for monitoring


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, check_db_connection
from config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    # Basic health check endpoint

    db_status = "connected" if check_db_connection() else "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }
   


@router.get("/")
async def root():
    # Root endpoint with API information

    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "documentation": "/docs",
        "health_check": "/health"
    }

