import sys
import os
from pathlib import Path

# CHANGED: We are now in 'api/', so the project root is just the parent directory.
# (Previously it was .parents[2])
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent 
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")