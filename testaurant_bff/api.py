import os
import sys
import json

# Add the current directory to sys.path so 'app' can be found during bundling
sys.path.append(os.path.dirname(__file__))

from app.main import app
from mangum import Mangum

# Wrapper to ensure 'handler' is clearly exported as a function
asgi_handler = Mangum(app, lifespan="on")

def handler(event, context):
    """Native Netlify Function handler wrapping FastAPI"""
    return asgi_handler(event, context)
