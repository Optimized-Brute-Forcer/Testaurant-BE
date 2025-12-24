import sys
import os
from pathlib import Path

# Path: netlify/functions/app_handler.py
# We need to go up 2 levels to find 'app' (file -> functions -> netlify -> ROOT)
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")