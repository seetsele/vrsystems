"""
Simple API Server Startup
Avoids uvicorn module path issues
"""
import sys
import os

# Set up paths
ROOT = r"c:\Users\lawm\Desktop\verity-systems"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "python-tools"))
os.chdir(os.path.join(ROOT, "python-tools"))

# Now import and run
import uvicorn
from api_server_v10 import app

if __name__ == "__main__":
    print("=" * 60)
    print("VERITY API SERVER - STARTING")
    print("=" * 60)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
