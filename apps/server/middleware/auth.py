"""
JWT Authentication Middleware for FastAPI

This module provides secure JWT token validation and user authentication
for the Todo App backend. It integrates with Better Auth JWT tokens.
"""

import os
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

# Load environment variables from .env file
load_dotenv()

# Environment variable for JWT secret
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable must be set")

# JWT algorithm (Better Auth typically uses HS256)
JWT_ALGORITHM = "HS256"

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:
    """
    FastAPI dependency to authenticate and return current user from JWT token.

    Verifies token signature, expiration, and extracts user information.
    Adds user to request.state.user for use in route handlers.

    Returns:
        Dict containing user 'id' and 'email'

    Raises:
        HTTPException: 401 for invalid/missing/expired tokens
    """
    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            credentials.credentials,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        # Extract user information from token
        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID"
            )

        # Create user dict
        user = {
            "id": user_id,
            "email": email or ""  # Email might be optional
        }

        # Add user to request state for use in route handlers
        request.state.user = user

        return user

    except JWTError as e:
        # Handle various JWT errors (expired, invalid signature, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


def verify_resource_ownership(resource_user_id: str, current_user: Dict[str, str]) -> None:
    """
    Verify that the current user owns the requested resource.

    Args:
        resource_user_id: The user_id associated with the resource
        current_user: The authenticated user dict from get_current_user

    Raises:
        HTTPException: 403 if user doesn't own the resource
    """
    if resource_user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )


# Example usage in route handlers:

"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from .middleware.auth import get_current_user, verify_resource_ownership
from .models import Task
from .schemas import TaskResponse

router = APIRouter()

@router.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    # Always filter by current user ID for security
    tasks = db.query(Task).filter(Task.user_id == current_user["id"]).all()
    return tasks

@router.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    verify_resource_ownership(task.user_id, current_user)

    return task

@router.post("/api/tasks", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    # Create task with current user's ID
    new_task = Task(
        user_id=current_user["id"],
        title=task_data.title,
        description=task_data.description
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    verify_resource_ownership(task.user_id, current_user)

    # Update task
    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/api/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    verify_resource_ownership(task.user_id, current_user)

    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
"""

# Error handling patterns:
"""
# In your main FastAPI app, you can add global exception handlers:

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# For additional security, you can add rate limiting, CORS, etc.
"""</content>
<parameter name="filePath">d:\todo-app\todo-app-phase-2\apps\server\middleware\auth.py