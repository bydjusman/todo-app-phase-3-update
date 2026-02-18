"""
Hugging Face Spaces entry point
This file is required for Hugging Face Spaces deployment
"""
from main import app

if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces uses PORT environment variable, default to 7860
    import os
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
