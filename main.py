# Railway Entry Point
# This redirects to the actual API server in python-tools

import sys
import os

# Add python-tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python-tools'))

# Import and run the app
from api_server_v9 import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
