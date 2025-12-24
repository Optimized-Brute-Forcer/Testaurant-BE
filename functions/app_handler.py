import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent 
sys.path.append(str(project_root))

from app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")