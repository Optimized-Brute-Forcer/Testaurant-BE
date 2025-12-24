import sys
import os
from pathlib import Path

# Calculate the path to the project root
# file -> functions -> netlify -> ROOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[2] 

# Add root to sys.path so we can import 'app'
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")