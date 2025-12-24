import sys
import os
from pathlib import Path

# File is in backend/app_handler.py -> Root is parent.parent
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent 
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")