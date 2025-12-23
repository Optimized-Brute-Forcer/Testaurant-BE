"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import Database
from app.controllers import auth_controller, organization_controller, bff_controller
from mangum import Mangum


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await Database.connect()
    yield
    # Shutdown
    await Database.disconnect()


app = FastAPI(
    title="Testaurant API",
    description="Automated testing platform for backend services",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_controller.router)
app.include_router(organization_controller.router)
app.include_router(bff_controller.router)

# Mangum handler for serverless deployment (Netlify/Lambda)
handler = Mangum(app)

# Health check
@app.get("/app/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "testaurant"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Testaurant API",
        "docs": "/docs",
        "health": "/app/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
