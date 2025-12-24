import sys
import os
from pathlib import Path

# Adjust path: file is in netlify/functions/ so root is 2 levels up
current_file = Path(__file__).resolve()
project_root = current_file.parents[2] 
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")