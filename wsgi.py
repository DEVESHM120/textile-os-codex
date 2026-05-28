import sys
import os

# Add backend/ to path so 'from api.routes import ...' resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from api.routes import create_app

app = create_app()
