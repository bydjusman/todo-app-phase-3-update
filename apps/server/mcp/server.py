"""
MCP (Model Context Protocol) server implementation for chatbot tools.
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from models.task import Task, TaskCreate, TaskUpdate
from models.models import Conversation, Message
from auth.jwt import get_current_user, TokenData
from database.session import get_db
import uuid
from datetime import datetime, timezone


class MCPServer:
    """
    MCP Server that registers and manages tools for the chatbot.
    """

    def __init__(self):
        self.tools = {}
        self.registered_functions = {}

    def register_tool(self, name: str):
        """
        Register an MCP tool with the server.
        This is a decorator factory that returns the actual decorator.
        """
        def decorator(func: callable):
            self.tools[name] = func
            self.registered_functions[name] = func
            return func
        return decorator

    def get_tool(self, name: str):
        """
        Get a registered tool by name.
        """
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """
        List all registered tools.
        """
        return list(self.tools.keys())


# Global MCP server instance
mcp_server = MCPServer()


def validate_user_access(user_id: str, target_user_id: str):
    """
    Validate that the authenticated user can access the target user's data.
    """
    if user_id != target_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this user's data"
        )


@mcp_server.register_tool("add_task")
async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str = "medium",
    db: Session = None
) -> Dict[str, Any]:
    """
    Creates a new task for the specified user.

    Args:
        user_id: ID of the user creating the task
        title: Title of the task (required)
        description: Detailed description of the task
        due_date: Due date in ISO 8601 format
        priority: Priority level (low, medium, high)
        db: Database session

    Returns:
        dict: Task object with ID and creation confirmation
    """
    try:
        # Create task data
        task_data = {
            "title": title,
            "description": description or None,
            "completed": False
        }

        # Add task to database
        db_task = Task(
            **task_data,
            user_id=user_id
        )

        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        return {
            "task_id": str(db_task.id),
            "title": db_task.title,
            "status": "pending",
            "created_at": db_task.created_at.isoformat(),
            "message": f"I've created the task '{db_task.title}' for you."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@mcp_server.register_tool("list_tasks")
async def list_tasks(
    user_id: str,
    status: str = "all",
    date_filter: str = "",
    limit: int = 10,
    offset: int = 0,
    db: Session = None
) -> Dict[str, Any]:
    """
    Retrieves user's tasks based on specified filters.

    Args:
        user_id: ID of the user requesting tasks
        status: Filter by status (all, pending, completed, overdue)
        date_filter: Filter by date (today, this_week, this_month, overdue, custom)
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip (for pagination)
        db: Database session

    Returns:
        dict: List of matching tasks and summary information
    """
    try:
        # Build the query
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status and status != "all":
            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

        # Apply date filter (basic implementation)
        if date_filter:
            if date_filter == "today":
                # Filter for tasks created today
                today = datetime.now(timezone.utc).date()
                query = query.where(Task.created_at >= today)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        tasks = db.exec(query).all()

        task_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "status": "completed" if task.completed else "pending",
                "due_date": getattr(task, 'due_date', None),
                "created_at": task.created_at.isoformat(),
                "description": task.description
            }
            task_list.append(task_dict)

        return {
            "tasks": task_list,
            "total_count": len(task_list),
            "message": f"You have {len(task_list)} tasks matching your criteria."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@mcp_server.register_tool("complete_task")
async def complete_task(
    user_id: str,
    task_id: str,
    db: Session = None
) -> Dict[str, Any]:
    """
    Marks a specified task as completed.

    Args:
        user_id: ID of the user updating the task
        task_id: ID of the task to mark as completed
        db: Database session

    Returns:
        dict: Updated task object and confirmation message
    """
    try:
        # Get the task
        task = db.get(Task, int(task_id))
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Validate user access
        validate_user_access(user_id, task.user_id)

        # Update task status
        task.completed = True
        task.updated_at = datetime.now(timezone.utc)

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "task": {
                "id": str(task.id),
                "title": task.title,
                "status": "completed",
                "completed_at": task.updated_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"Great job! I've marked '{task.title}' as completed."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing task: {str(e)}")


@mcp_server.register_tool("delete_task")
async def delete_task(
    user_id: str,
    task_id: str,
    confirmation: bool = False,
    db: Session = None
) -> Dict[str, Any]:
    """
    Deletes a specified task after optional confirmation.

    Args:
        user_id: ID of the user deleting the task
        task_id: ID of the task to delete
        confirmation: Flag indicating user confirmation (for sensitive operations)
        db: Database session

    Returns:
        dict: Deletion confirmation and details
    """
    try:
        # Get the task
        task = db.get(Task, int(task_id))
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Validate user access
        validate_user_access(user_id, task.user_id)

        # Delete the task
        db.delete(task)
        db.commit()

        return {
            "task_id": str(task.id),
            "message": f"I've removed the task '{task.title}' from your list.",
            "deleted_at": datetime.now(timezone.utc).isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@mcp_server.register_tool("update_task")
async def update_task(
    user_id: str,
    task_id: str,
    title: str = "",
    description: str = "",
    due_date: str = "",
    priority: str = "",
    status: str = "",
    db: Session = None
) -> Dict[str, Any]:
    """
    Updates properties of an existing task.

    Args:
        user_id: ID of the user updating the task
        task_id: ID of the task to update
        title: New task title
        description: New task description
        due_date: New due date in ISO 8601 format
        priority: New priority level
        status: New task status
        db: Database session

    Returns:
        dict: Updated task object and confirmation message
    """
    try:
        # Get the task
        task = db.get(Task, int(task_id))
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Validate user access
        validate_user_access(user_id, task.user_id)

        # Prepare update data
        update_data = {}
        if title:
            update_data["title"] = title
        if description:
            update_data["description"] = description
        if status:
            update_data["completed"] = (status.lower() == 'completed')

        # Update task with provided values
        for field, value in update_data.items():
            setattr(task, field, value)
        task.updated_at = datetime.now(timezone.utc)

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "task": {
                "id": str(task.id),
                "title": task.title,
                "status": "completed" if task.completed else "pending",
                "due_date": getattr(task, 'due_date', None),
                "description": task.description,
                "priority": getattr(task, 'priority', 'medium'),
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"I've updated the task '{task.title}'."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


def get_mcp_server():
    """
    Dependency to get the MCP server instance.
    """
    return mcp_server