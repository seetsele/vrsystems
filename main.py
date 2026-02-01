# =============================================================================
# Verity Systems - Main Entry Point
# =============================================================================
# Production Railway/Cloud deployment entry
# Routes to the latest stable API server (v10/v11)
# =============================================================================

import sys
import os
from pathlib import Path

# Ensure python-tools is on path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "python-tools"))
sys.path.insert(0, str(PROJECT_ROOT))

# Import the production API app
try:
    from api_server_v10 import app
except ImportError:
    # Fallback to v9 if v10 not available
    from api_server_v9 import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    workers = int(os.getenv("WORKERS", 1))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info",
        access_log=True,
    )
