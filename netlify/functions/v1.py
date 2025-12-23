from app.main import app
from mangum import Mangum

# Explicit handler for Netlify with lifespan enabled for DB connection
handler = Mangum(app, lifespan="on")

@app.get("/test-path")
async def test_path():
    return {"message": "V1 path routing is working!"}
