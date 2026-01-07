#!/usr/bin/env python3
"""
RiskSpeak Backend Server
Run this script to start the FastAPI server
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Server")
    print("=" * 60)
    print(f"Host: {settings.HOST}")
    print(f"Port: {settings.PORT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )