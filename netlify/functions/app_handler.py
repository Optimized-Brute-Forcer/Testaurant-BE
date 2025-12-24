import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.main import app
from mangum import Mangum

asgi_handler = Mangum(app, lifespan="on")

def handler(event, context):
    return asgi_handler(event, context)
