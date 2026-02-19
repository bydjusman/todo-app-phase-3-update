# MCP Tools Specification

## Overview
This document defines the MCP (Model Context Protocol) tools that will be available for the AI chatbot to perform task management operations. These tools will be registered with the MCP server and called by the OpenAI Agents SDK based on natural language processing results.

## Available MCP Tools

### @tools/add_task
Creates a new task with provided information.

**Function Signature**:
```python
def add_task(
    user_id: str,
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str = "medium"
) -> dict:
    """
    Creates a new task for the specified user

    Args:
        user_id: ID of the user creating the task
        title: Title of the task (required)
        description: Detailed description of the task
        due_date: Due date in ISO 8601 format
        priority: Priority level (low, medium, high)

    Returns:
        dict: Task object with ID and creation confirmation
    """
```

**Parameters**:
- `user_id` (string, required): The authenticated user ID
- `title` (string, required): The task title extracted from natural language
- `description` (string, optional): Detailed task description
- `due_date` (string, optional): Task due date in ISO 8601 format
- `priority` (string, optional): Task priority level (default: "medium")

**Return Schema**:
```json
{
  "task_id": "ID of the newly created task",
  "title": "Task title",
  "status": "pending",
  "created_at": "ISO 8601 timestamp",
  "message": "Confirmation message for the user"
}
```

**Example Input**:
```json
{
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Get milk, bread, and eggs",
  "due_date": "2026-02-20T10:00:00Z",
  "priority": "high"
}
```

**Example Output**:
```json
{
  "task_id": "task-456",
  "title": "Buy groceries",
  "status": "pending",
  "created_at": "2026-02-19T14:30:00Z",
  "message": "I've created the task 'Buy groceries' for you."
}
```

**Error Cases**:
- Missing required `user_id` or `title` parameters
- Invalid date format for `due_date`
- Unauthorized access (user_id does not match authenticated user)
- Validation errors for parameter values

### @tools/list_tasks
Retrieves user's tasks based on filters.

**Function Signature**:
```python
def list_tasks(
    user_id: str,
    status: str = "all",
    date_filter: str = "",
    limit: int = 10,
    offset: int = 0
) -> dict:
    """
    Retrieves user's tasks based on specified filters

    Args:
        user_id: ID of the user requesting tasks
        status: Filter by status (all, pending, completed, overdue)
        date_filter: Filter by date (today, this_week, this_month, overdue, custom)
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip (for pagination)

    Returns:
        dict: List of matching tasks and summary information
    """
```

**Parameters**:
- `user_id` (string, required): The authenticated user ID
- `status` (string, optional): Task status filter (all, pending, completed, overdue)
- `date_filter` (string, optional): Date-based filter
- `limit` (integer, optional): Maximum number of tasks to return (default: 10)
- `offset` (integer, optional): Number of tasks to skip for pagination (default: 0)

**Return Schema**:
```json
{
  "tasks": [
    {
      "id": "Task ID",
      "title": "Task title",
      "status": "Task status",
      "due_date": "Due date if applicable",
      "created_at": "Task creation timestamp",
      "description": "Task description if available"
    }
  ],
  "total_count": "Total number of tasks matching criteria",
  "message": "Summary message for the user"
}
```

**Example Input**:
```json
{
  "user_id": "user-123",
  "status": "pending",
  "date_filter": "today",
  "limit": 5
}
```

**Example Output**:
```json
{
  "tasks": [
    {
      "id": "task-456",
      "title": "Buy groceries",
      "status": "pending",
      "due_date": "2026-02-20T10:00:00Z",
      "created_at": "2026-02-19T14:30:00Z",
      "description": "Get milk, bread, and eggs"
    }
  ],
  "total_count": 1,
  "message": "You have 1 pending task for today."
}
```

**Error Cases**:
- Missing required `user_id` parameter
- Unauthorized access (user_id does not match authenticated user)
- Invalid status or date_filter values
- Invalid limit/offset values

### @tools/complete_task
Marks a task as completed.

**Function Signature**:
```python
def complete_task(
    user_id: str,
    task_id: str
) -> dict:
    """
    Marks a specified task as completed

    Args:
        user_id: ID of the user updating the task
        task_id: ID of the task to mark as completed

    Returns:
        dict: Updated task object and confirmation message
    """
```

**Parameters**:
- `user_id` (string, required): The authenticated user ID
- `task_id` (string, required): ID of the task to complete

**Return Schema**:
```json
{
  "task": {
    "id": "Updated task ID",
    "title": "Updated task title",
    "status": "completed",
    "completed_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  },
  "message": "Confirmation message for the user"
}
```

**Example Input**:
```json
{
  "user_id": "user-123",
  "task_id": "task-456"
}
```

**Example Output**:
```json
{
  "task": {
    "id": "task-456",
    "title": "Buy groceries",
    "status": "completed",
    "completed_at": "2026-02-19T15:00:00Z",
    "updated_at": "2026-02-19T15:00:00Z"
  },
  "message": "Great job! I've marked 'Buy groceries' as completed."
}
```

**Error Cases**:
- Missing required `user_id` or `task_id` parameters
- Unauthorized access (user_id does not match authenticated user or task doesn't belong to user)
- Task already completed
- Task does not exist

### @tools/delete_task
Deletes a specified task.

**Function Signature**:
```python
def delete_task(
    user_id: str,
    task_id: str,
    confirmation: bool = false
) -> dict:
    """
    Deletes a specified task after optional confirmation

    Args:
        user_id: ID of the user deleting the task
        task_id: ID of the task to delete
        confirmation: Flag indicating user confirmation (for sensitive operations)

    Returns:
        dict: Deletion confirmation and details
    """
```

**Parameters**:
- `user_id` (string, required): The authenticated user ID
- `task_id` (string, required): ID of the task to delete
- `confirmation` (boolean, optional): Confirmation flag for destructive operations

**Return Schema**:
```json
{
  "task_id": "ID of deleted task",
  "message": "Confirmation message for the user",
  "deleted_at": "ISO 8601 timestamp of deletion"
}
```

**Example Input**:
```json
{
  "user_id": "user-123",
  "task_id": "task-456",
  "confirmation": true
}
```

**Example Output**:
```json
{
  "task_id": "task-456",
  "message": "I've removed the task 'Buy groceries' from your list.",
  "deleted_at": "2026-02-19T15:15:00Z"
}
```

**Error Cases**:
- Missing required `user_id` or `task_id` parameters
- Unauthorized access (user_id does not match authenticated user or task doesn't belong to user)
- Task does not exist
- Missing confirmation for deletion operation

### @tools/update_task
Updates properties of an existing task.

**Function Signature**:
```python
def update_task(
    user_id: str,
    task_id: str,
    title: str = "",
    description: str = "",
    due_date: str = "",
    priority: str = "",
    status: str = ""
) -> dict:
    """
    Updates properties of an existing task

    Args:
        user_id: ID of the user updating the task
        task_id: ID of the task to update
        title: New task title
        description: New task description
        due_date: New due date in ISO 8601 format
        priority: New priority level
        status: New task status

    Returns:
        dict: Updated task object and confirmation message
    """
```

**Parameters**:
- `user_id` (string, required): The authenticated user ID
- `task_id` (string, required): ID of the task to update
- `title` (string, optional): New task title
- `description` (string, optional): New task description
- `due_date` (string, optional): New due date in ISO 8601 format
- `priority` (string, optional): New priority level
- `status` (string, optional): New task status

**Return Schema**:
```json
{
  "task": {
    "id": "Updated task ID",
    "title": "Updated task title",
    "status": "Updated status",
    "due_date": "Updated due date",
    "description": "Updated description",
    "priority": "Updated priority",
    "updated_at": "ISO 8601 timestamp"
  },
  "message": "Confirmation message for the user"
}
```

**Example Input**:
```json
{
  "user_id": "user-123",
  "task_id": "task-456",
  "due_date": "2026-02-21T10:00:00Z",
  "priority": "low"
}
```

**Example Output**:
```json
{
  "task": {
    "id": "task-456",
    "title": "Buy groceries",
    "status": "pending",
    "due_date": "2026-02-21T10:00:00Z",
    "description": "Get milk, bread, and eggs",
    "priority": "low",
    "updated_at": "2026-02-19T15:30:00Z"
  },
  "message": "I've updated the due date and priority for 'Buy groceries'."
}
```

**Error Cases**:
- Missing required `user_id` or `task_id` parameters
- Unauthorized access (user_id does not match authenticated user or task doesn't belong to user)
- Task does not exist
- Invalid date format for `due_date`
- Invalid status or priority values
- No parameters provided to update

## MCP Server Implementation Requirements

### Tool Registration
- All tools must be registered with the MCP server at initialization
- Tools must include proper type hints and documentation
- Authentication middleware must validate user_id for each tool call

### Authentication & Authorization
- Each tool call must validate that the user_id is authenticated
- Tools must verify that users can only operate on their own tasks
- Proper error responses must be returned for unauthorized access

### Error Handling
- Tools must handle validation errors gracefully
- Database connection issues should return appropriate error messages
- Invalid parameters should return descriptive error messages