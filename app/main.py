"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import Database
from app.controllers import auth_controller, organization_controller, bff_controller
from mangum import Mangum
import markdown
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import os


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

# Templates
templates = Jinja2Templates(directory="app/templates")

# Health check
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Testaurant API",
        "docs": "/docs",
        "health": "/app/health",
        "lld": "/lld"
    }

@app.get("/lld", response_class=HTMLResponse)
async def get_lld(request: Request):
    """Serve LLD documentation."""
    lld_path = "app/docs/lld.md"
    if not os.path.exists(lld_path):
        return "LLD documentation not found."
    
    with open(lld_path, "r") as f:
        content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite', 'tables'])
    
    return templates.TemplateResponse("lld.html", {"request": request, "content": html_content})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
