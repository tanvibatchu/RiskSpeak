from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import portfolio, analysis, brokers
from app.config import settings

app = FastAPI(
    title="RiskSpeak API",
    description="Portfolio risk analysis and management API",
    version="1.0.0"
)

# CORS middleware - adjust origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio.router)
app.include_router(analysis.router)
app.include_router(brokers.router)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "RiskSpeak API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "portfolio": "/api/portfolio",
            "analysis": "/api/analysis",
            "brokers": "/api/brokers",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "development" if settings.DEBUG else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )