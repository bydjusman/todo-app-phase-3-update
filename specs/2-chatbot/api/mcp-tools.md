# API Specification: MCP Tools for Chatbot

## Overview
This specification defines the MCP (Model Context Protocol) tools that will be available for the AI chatbot to perform task management operations. These tools will be registered with the MCP server and called by the OpenAI Agents SDK based on natural language processing results.

## Available MCP Tools

### @tools/create_task
Creates a new task with provided information.

**Function Signature**:
```python
def create_task(
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

**Response**:
```json
{
  "task_id": "ID of the newly created task",
  "title": "Task title",
  "status": "pending",
  "created_at": "ISO 8601 timestamp",
  "message": "Confirmation message for the user"
}
```

### @tools/get_tasks
Retrieves user's tasks based on filters.

**Function Signature**:
```python
def get_tasks(
    user_id: str,
    status: str = "all",
    date_filter: str = "",
    limit: int = 10
) -> dict:
    """
    Retrieves user's tasks based on specified filters

    Args:
        user_id: ID of the user requesting tasks
        status: Filter by status (all, pending, completed, overdue)
        date_filter: Filter by date (today, this_week, this_month, overdue, custom)
        limit: Maximum number of tasks to return

    Returns:
        dict: List of matching tasks and summary information
    """
```

**Parameters**:
- `user_id` (string, required): The authenticated user ID
- `status` (string, optional): Task status filter (all, pending, completed, overdue)
- `date_filter` (string, optional): Date-based filter
- `limit` (integer, optional): Maximum number of tasks to return (default: 10)

**Response**:
```json
{
  "tasks": [
    {
      "id": "Task ID",
      "title": "Task title",
      "status": "Task status",
      "due_date": "Due date if applicable",
      "created_at": "Task creation timestamp"
    }
  ],
  "total_count": "Total number of tasks matching criteria",
  "message": "Summary message for the user"
}
```

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
    status: str = "",
    priority: str = ""
) -> dict:
    """
    Updates properties of an existing task

    Args:
        user_id: ID of the user updating the task
        task_id: ID of the task to update
        title: New task title
        description: New task description
        due_date: New due date in ISO 8601 format
        status: New status (pending, completed)
        priority: New priority level

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
- `status` (string, optional): New task status
- `priority` (string, optional): New priority level

**Response**:
```json
{
  "task": {
    "id": "Updated task ID",
    "title": "Updated task title",
    "status": "Updated status",
    "due_date": "Updated due date",
    "updated_at": "ISO 8601 timestamp"
  },
  "message": "Confirmation message for the user"
}
```

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

**Response**:
```json
{
  "task_id": "ID of deleted task",
  "message": "Confirmation message for the user",
  "deleted_at": "ISO 8601 timestamp of deletion"
}
```

### @tools/parse_intent
Parses natural language to determine user intent and extract entities.

**Function Signature**:
```python
def parse_intent(
    user_input: str
) -> dict:
    """
    Parses natural language input to identify intent and extract entities

    Args:
        user_input: Raw natural language input from user

    Returns:
        dict: Parsed intent and extracted entities
    """
```

**Parameters**:
- `user_input` (string, required): The raw natural language input

**Response**:
```json
{
  "intent": "Identified intent (create_task, get_tasks, update_task, delete_task)",
  "entities": {
    "task_title": "Extracted task title if applicable",
    "due_date": "Extracted due date in ISO 8601 if applicable",
    "task_id": "ID of specific task if referenced",
    "status_filter": "Status filter if applicable",
    "priority": "Priority level if specified"
  },
  "confidence": "Confidence score of the parsing (0.0 to 1.0)"
}
```

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

## Success Criteria
- All MCP tools are registered and callable through the OpenAI Agents SDK
- Tools process 95% of valid requests successfully
- Authentication validation works for 100% of tool calls
- Error handling provides useful feedback for 100% of failure scenarios