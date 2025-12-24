import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.main import app
from mangum import Mangum

asgi_handler = Mangum(app, lifespan="on")

def handler(event, context):
    return asgi_handler(event, context)
