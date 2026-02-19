from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import tasks
from api.routes import auth
from api.routes import chat
import traceback

app = FastAPI(title="Todo API", version="1.0.0")

# Add CORS middleware - allow all origins for Hugging Face deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the task routes with API prefix
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

# Include the auth routes with API prefix
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Include the chat routes - no prefix since it uses user_id in path
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Exception occurred: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"message": f"Internal server error: {str(exc)}"}
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"===== Application Startup at {__import__('datetime').datetime.now()} =====")
    print(f"Starting server on http://0.0.0.0:{port}")
    
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)