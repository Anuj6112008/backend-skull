import sys
from pathlib import Path

# Ensure the api/ directory is on the path so "app" can be imported on Vercel
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app
