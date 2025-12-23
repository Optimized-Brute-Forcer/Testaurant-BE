import os
import sys

# Add the current directory to sys.path so 'app' can be found during bundling
sys.path.append(os.path.dirname(__file__))

from app.main import app
from mangum import Mangum

# Explicit handler for Netlify with lifespan enabled for DB connection
handler = Mangum(app, lifespan="on")

@app.get("/test-path")
async def test_path():
    return {"message": "V1 path routing is working!"}

@app.get("/debug")
async def debug_event(event: dict = None):
    return {"message": "Debug event", "event": event}
