import sys
import os
from pathlib import Path

# CURRENT PATH: /opt/build/repo/api/app_handler.py
# TARGET ROOT:  /opt/build/repo/

# We need to go up 2 levels (file -> api -> root) 
# OR just 1 level depending on how python sees it. 
# This standard robust fix handles both:
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")