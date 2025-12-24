import sys
import os
from pathlib import Path

# Add the project root to sys.path so we can import 'app'
# We look for the folder containing 'app' relative to this file
current_file = Path(__file__).resolve()
project_root = current_file.parents[2] # Adjusts based on netlify/functions/ structure
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

# lifespan="off" is safer for Serverless to prevent DB connection timeouts 
# during the freeze/thaw cycle of Lambda. 
# Once basic deployment works, you can try "on" or "auto".
handler = Mangum(app, lifespan="off")