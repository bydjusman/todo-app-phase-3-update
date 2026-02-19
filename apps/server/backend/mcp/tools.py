"""
MCP Tools for Task Management

This module defines MCP tools that allow natural language interaction with the task management system.
Each tool properly authenticates the user using JWT and ensures user data isolation.
"""
from typing import List, Optional
from datetime import datetime
from fastmcp import FastMCP
from fastmcp.types import Tool
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Import the required dependencies from the existing application
from ...auth.jwt import verify_token
from ...models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ...database.session import get_db, engine
from sqlmodel import Session


class TaskCreateRequest(BaseModel):
    """Request model for creating a task"""
    title: str = Field(..., description="Task title, 1-200 characters")
    description: Optional[str] = Field(None, description="Optional task description")
    completed: bool = Field(default=False, description="Whether the task is completed, defaults to false")


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task"""
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, description="New title for the task")
    description: Optional[str] = Field(None, description="New description for the task")
    completed: Optional[bool] = Field(None, description="New completion status for the task")


class TaskToggleCompletionRequest(BaseModel):
    """Request model for toggling task completion"""
    task_id: int = Field(..., description="ID of the task to toggle")
    completed: bool = Field(..., description="Whether the task should be completed")


class TaskGetRequest(BaseModel):
    """Request model for getting a specific task"""
    task_id: int = Field(..., description="ID of the task to retrieve")


class TaskListRequest(BaseModel):
    """Request model for listing tasks"""
    status: Optional[str] = Field(None, description="Filter by completion status: all, pending, completed")
    sort: Optional[str] = Field("-created_at", description="Sort by field: created_at, -created_at, title, -title")
    page: int = Field(1, description="Page number for pagination")
    limit: int = Field(20, description="Number of tasks per page")


# Initialize FastMCP
mcp = FastMCP(
    name="task-management-tools",
    description="Tools for managing user tasks through natural language commands"
)


@contextmanager
def get_db_context():
    """Context manager to properly handle database sessions"""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


@mcp.tool(
    name="create_task",
    description="Create a new task for the authenticated user",
    parameters=TaskCreateRequest
)
def create_task_mcp(
    token: str,
    title: str,
    description: Optional[str] = None,
    completed: bool = False
) -> dict:
    """
    MCP tool to create a new task using the existing backend logic.
    """
    # Verify the user token to get user information
    token_data = verify_token(token)
    if not token_data:
        return {"error": "Invalid token or unauthorized"}

    with get_db_context() as db:
        try:
            # Prepare the task creation request and create the task directly
            # (replicating the logic from the original create_task function)
            db_task = Task(
                title=title,
                description=description,
                completed=completed,
                user_id=token_data.user_id
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)

            return {
                "success": True,
                "task": db_task.dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


@mcp.tool(
    name="get_task",
    description="Get a specific task by ID for the authenticated user",
    parameters=TaskGetRequest
)
def get_task_mcp(
    token: str,
    task_id: int
) -> dict:
    """
    MCP tool to get a specific task using the existing backend logic.
    """
    # Verify the user token to get user information
    token_data = verify_token(token)
    if not token_data:
        return {"error": "Invalid token or unauthorized"}

    with get_db_context() as db:
        try:
            # Replicate the logic from the original get_task function
            task = db.get(Task, task_id)
            if not task:
                return {"success": False, "error": "Task not found"}

            # Check ownership
            if task.user_id != token_data.user_id:
                return {"success": False, "error": "Not authorized to access this task"}

            return {
                "success": True,
                "task": task.dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


@mcp.tool(
    name="list_tasks",
    description="Get all tasks for the authenticated user with filtering and pagination",
    parameters=TaskListRequest
)
def list_tasks_mcp(
    token: str,
    status: Optional[str] = None,
    sort: Optional[str] = "-created_at",
    page: int = 1,
    limit: int = 20
) -> dict:
    """
    MCP tool to list tasks using the existing backend logic.
    """
    # Verify the user token to get user information
    token_data = verify_token(token)
    if not token_data:
        return {"error": "Invalid token or unauthorized"}

    with get_db_context() as db:
        try:
            # Build the query (replicating the logic from the original list_tasks function)
            from sqlmodel import select

            query = select(Task).where(Task.user_id == token_data.user_id)

            # Apply status filter
            if status and status != "all":
                if status == "pending":
                    query = query.where(Task.completed == False)
                elif status == "completed":
                    query = query.where(Task.completed == True)

            # Apply sorting
            if sort:
                if sort == "created_at":
                    query = query.order_by(Task.created_at)
                elif sort == "-created_at":
                    query = query.order_by(Task.created_at.desc())
                elif sort == "title":
                    query = query.order_by(Task.title)
                elif sort == "-title":
                    query = query.order_by(Task.title.desc())

            # Apply pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            tasks = db.exec(query).all()

            return {
                "success": True,
                "tasks": [task.dict() for task in tasks]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


@mcp.tool(
    name="update_task",
    description="Update a specific task for the authenticated user",
    parameters=TaskUpdateRequest
)
def update_task_mcp(
    token: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> dict:
    """
    MCP tool to update a task using the existing backend logic.
    """
    # Verify the user token to get user information
    token_data = verify_token(token)
    if not token_data:
        return {"error": "Invalid token or unauthorized"}

    with get_db_context() as db:
        try:
            # Replicate the logic from the original update_task function
            db_task = db.get(Task, task_id)
            if not db_task:
                return {"success": False, "error": "Task not found"}

            # Check ownership
            if db_task.user_id != token_data.user_id:
                return {"success": False, "error": "Not authorized to update this task"}

            # Update the task with provided values
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if completed is not None:
                update_data["completed"] = completed

            for field, value in update_data.items():
                setattr(db_task, field, value)

            db.add(db_task)
            db.commit()
            db.refresh(db_task)

            return {
                "success": True,
                "task": db_task.dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


@mcp.tool(
    name="delete_task",
    description="Delete a specific task for the authenticated user",
    parameters=TaskGetRequest
)
def delete_task_mcp(
    token: str,
    task_id: int
) -> dict:
    """
    MCP tool to delete a task using the existing backend logic.
    """
    # Verify the user token to get user information
    token_data = verify_token(token)
    if not token_data:
        return {"error": "Invalid token or unauthorized"}

    with get_db_context() as db:
        try:
            # Replicate the logic from the original delete_task function
            task = db.get(Task, task_id)
            if not task:
                return {"success": False, "error": "Task not found"}

            # Check ownership
            if task.user_id != token_data.user_id:
                return {"success": False, "error": "Not authorized to delete this task"}

            db.delete(task)
            db.commit()

            return {
                "success": True,
                "message": "Task deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


@mcp.tool(
    name="toggle_task_completion",
    description="Toggle the completion status of a task for the authenticated user",
    parameters=TaskToggleCompletionRequest
)
def toggle_task_completion_mcp(
    token: str,
    task_id: int,
    completed: bool
) -> dict:
    """
    MCP tool to toggle task completion using the existing backend logic.
    """
    # Verify the user token to get user information
    token_data = verify_token(token)
    if not token_data:
        return {"error": "Invalid token or unauthorized"}

    with get_db_context() as db:
        try:
            # Replicate the logic from the original toggle_task_completion function
            task = db.get(Task, task_id)
            if not task:
                return {"success": False, "error": "Task not found"}

            # Check ownership
            if task.user_id != token_data.user_id:
                return {"success": False, "error": "Not authorized to update this task"}

            task.completed = completed
            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "success": True,
                "task": task.dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Export the mcp instance
__all__ = ["mcp"]