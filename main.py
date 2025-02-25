import os
import uvicorn
from api import app  # Import app from api.py

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
