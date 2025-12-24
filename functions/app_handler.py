import sys
import os
from pathlib import Path

# Adjust path: The root is now just 1 level up (parent), not 2
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent 
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")