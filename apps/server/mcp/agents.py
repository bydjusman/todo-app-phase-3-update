"""
OpenAI Agents SDK integration for the chatbot.
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
import os
from sqlmodel import Session
from .server import mcp_server
from models.models import Message, Conversation
from database.session import get_db
from auth.jwt import get_current_user, TokenData
import uuid
from datetime import datetime, timezone


class OpenAIAgentsIntegration:
    """
    Integration layer between OpenAI Agents SDK and MCP tools.
    """

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.mcp_server = mcp_server

    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Execute an MCP tool with the provided arguments.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Get database session
        db = next(get_db())
        try:
            # Get the tool function
            tool_func = self.mcp_server.get_tool(tool_name)
            if not tool_func:
                return {
                    "error": f"Tool {tool_name} not found",
                    "message": f"Tool {tool_name} not found"
                }

            # Add database session to tool arguments
            tool_args_with_db = tool_args.copy()
            tool_args_with_db['db'] = db
            tool_args_with_db['user_id'] = user_id

            # Execute the tool asynchronously
            if asyncio.iscoroutinefunction(tool_func):
                # Run in a new event loop in a separate thread
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, tool_func(**tool_args_with_db))
                    result = future.result()
            else:
                result = tool_func(**tool_args_with_db)

            return result
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Error executing tool: {str(e)}"
            }
        finally:
            db.close()

    def process_conversation(self, user_input: str, user_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user's natural language input using OpenAI and MCP tools.
        """
        # Create or use existing conversation
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        # This is a simplified implementation - in a real implementation,
        # we would use OpenAI's assistant API or functions to determine intent
        # and call appropriate tools.

        # For now, we'll implement a basic intent recognition
        result = self._recognize_intent_and_execute(user_input, user_id)

        # Add conversation context to result
        result["context"] = {
            "conversation_id": conversation_id
        }

        return result

    def _recognize_intent_and_execute(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Enhanced intent recognition and tool execution with better task ID/title extraction.
        """
        user_input_lower = user_input.lower()
        print(f"DEBUG: Processing user input: '{user_input_lower}' for user_id: {user_id}")  # Debug log

        # Pattern matching for task creation
        if any(word in user_input_lower for word in ["create", "add", "new", "make"]):
            print(f"DEBUG: Detected creation intent")  # Debug log
            # Extract task title (simple extraction)
            title = self._extract_task_title(user_input)
            print(f"DEBUG: Extracted title: '{title}'")  # Debug log
            if title:
                return self.execute_tool("add_task", {"title": title}, user_id)

        # Pattern matching for task listing
        elif any(word in user_input_lower for word in ["list", "show", "get", "what", "have"]):
            print(f"DEBUG: Detected listing intent")  # Debug log
            # Check if asking for completed tasks
            if any(word in user_input_lower for word in ["completed", "done", "finished"]):
                return self.execute_tool("list_tasks", {"status": "completed"}, user_id)
            elif any(word in user_input_lower for word in ["pending", "todo", "not done"]):
                return self.execute_tool("list_tasks", {"status": "pending"}, user_id)
            else:
                return self.execute_tool("list_tasks", {"status": "all"}, user_id)

        # Pattern matching for task completion
        elif any(word in user_input_lower for word in ["complete", "finish", "done", "mark"]):
            print(f"DEBUG: Detected completion intent")  # Debug log
            # Extract task by title from user input
            task_title = self._extract_task_title_from_command(user_input_lower)
            print(f"DEBUG: Extracted task title for completion: '{task_title}'")  # Debug log
            if task_title:
                # First, get the user's tasks to find the matching one
                tasks_result = self.execute_tool("list_tasks", {"status": "all"}, user_id)
                print(f"DEBUG: Got {len(tasks_result.get('tasks', []))} tasks from list_tasks")  # Debug log
                if "tasks" in tasks_result:
                    matching_task = self._find_task_by_title(tasks_result["tasks"], task_title, user_id)
                    print(f"DEBUG: Matching task found: {matching_task is not None}")  # Debug log
                    if matching_task:
                        print(f"DEBUG: Calling complete_task with task_id: {matching_task['id']}")  # Debug log
                        return self.execute_tool("complete_task", {"task_id": str(matching_task["id"])}, user_id)
                    else:
                        print(f"DEBUG: No matching task found for title '{task_title}', showing available tasks")  # Debug log
                        return {
                            "message": f"I couldn't find a task with title '{task_title}' in your list. Here are your current tasks:",
                            "tasks": tasks_result["tasks"],
                            "intent": "list_tasks"
                        }
                else:
                    print(f"DEBUG: No tasks found in tasks_result")  # Debug log
                    return {
                        "message": f"I couldn't find a task with title '{task_title}' in your list.",
                        "intent": "unknown"
                    }
            else:
                print(f"DEBUG: Could not extract task title for completion")  # Debug log
                # If we can't extract a specific task, ask for clarification
                return {
                    "message": "To complete a task, please specify which task you want to mark as completed (e.g., 'Complete the grocery shopping task').",
                    "intent": "unknown"
                }

        # Pattern matching for task deletion
        elif any(word in user_input_lower for word in ["delete", "remove", "cancel"]):
            print(f"DEBUG: Detected deletion intent")  # Debug log
            # Extract task by title from user input
            task_title = self._extract_task_title_from_command(user_input_lower)
            print(f"DEBUG: Extracted task title for deletion: '{task_title}'")  # Debug log
            if task_title:
                # First, get the user's tasks to find the matching one
                tasks_result = self.execute_tool("list_tasks", {"status": "all"}, user_id)
                print(f"DEBUG: Got {len(tasks_result.get('tasks', []))} tasks from list_tasks")  # Debug log
                if "tasks" in tasks_result:
                    matching_task = self._find_task_by_title(tasks_result["tasks"], task_title, user_id)
                    print(f"DEBUG: Matching task found for deletion: {matching_task is not None}")  # Debug log
                    if matching_task:
                        print(f"DEBUG: Calling delete_task with task_id: {matching_task['id']}")  # Debug log
                        return self.execute_tool("delete_task", {"task_id": str(matching_task["id"])}, user_id)
                    else:
                        print(f"DEBUG: No matching task found for title '{task_title}', showing available tasks")  # Debug log
                        return {
                            "message": f"I couldn't find a task with title '{task_title}' in your list. Here are your current tasks:",
                            "tasks": tasks_result["tasks"],
                            "intent": "list_tasks"
                        }
                else:
                    print(f"DEBUG: No tasks found in tasks_result")  # Debug log
                    return {
                        "message": f"I couldn't find a task with title '{task_title}' in your list.",
                        "intent": "unknown"
                    }
            else:
                print(f"DEBUG: Could not extract task title for deletion")  # Debug log
                # If we can't extract a specific task, ask for clarification
                return {
                    "message": "To delete a task, please specify which task you want to remove (e.g., 'Delete the grocery shopping task').",
                    "intent": "unknown"
                }

        # Pattern matching for task updates
        elif any(word in user_input_lower for word in ["update", "change", "edit", "modify"]):
            print(f"DEBUG: Detected update intent")  # Debug log
            # Extract task by title from user input
            task_title = self._extract_task_title_from_command(user_input_lower)
            print(f"DEBUG: Extracted task title for update: '{task_title}'")  # Debug log
            if task_title:
                # First, get the user's tasks to find the matching one
                tasks_result = self.execute_tool("list_tasks", {"status": "all"}, user_id)
                print(f"DEBUG: Got {len(tasks_result.get('tasks', []))} tasks from list_tasks")  # Debug log
                if "tasks" in tasks_result:
                    matching_task = self._find_task_by_title(tasks_result["tasks"], task_title, user_id)
                    print(f"DEBUG: Matching task found for update: {matching_task is not None}")  # Debug log
                    if matching_task:
                        # For now, just mark as completed if the request is about completion
                        if any(word in user_input_lower for word in ["complete", "finish", "done"]):
                            print(f"DEBUG: Calling complete_task with task_id: {matching_task['id']} for update intent")  # Debug log
                            return self.execute_tool("complete_task", {"task_id": str(matching_task["id"])}, user_id)
                        else:
                            print(f"DEBUG: Returning update task prompt")  # Debug log
                            return {
                                "message": f"I can update the '{task_title}' task. What changes would you like to make?",
                                "task": matching_task,
                                "intent": "update_task"
                            }
                    else:
                        print(f"DEBUG: No matching task found for title '{task_title}' in update flow")  # Debug log
                        return {
                            "message": f"I couldn't find a task with title '{task_title}' in your list. Here are your current tasks:",
                            "tasks": tasks_result["tasks"],
                            "intent": "list_tasks"
                        }
                else:
                    print(f"DEBUG: No tasks found in tasks_result for update flow")  # Debug log
                    return {
                        "message": f"I couldn't find a task with title '{task_title}' in your list.",
                        "intent": "unknown"
                    }
            else:
                print(f"DEBUG: Could not extract task title for update")  # Debug log
                # If we can't extract a specific task, ask for clarification
                return {
                    "message": "To update a task, please specify which task and what changes you want to make (e.g., 'Update the grocery shopping task to be completed').",
                    "intent": "unknown"
                }

        else:
            print(f"DEBUG: Unknown intent for input: '{user_input_lower}'")  # Debug log
            # Unknown intent
            return {
                "message": f"I'm not sure how to help with '{user_input}'. You can ask me to create, list, complete, or delete tasks.",
                "intent": "unknown"
            }

    def _extract_task_title(self, user_input: str) -> Optional[str]:
        """
        Simple task title extraction from user input.
        This is a basic implementation - a real implementation would use NLP.
        """
        # Remove common phrases
        user_input = user_input.lower()

        # Look for patterns like "create task to X" or "add task X"
        import re

        # Pattern 1: "create task to buy groceries" -> "buy groceries"
        match = re.search(r'(?:create|add|make|new)\s+(?:task|a task)\s+(?:to|that|which)\s+(.+?)(?:\s+for\s+tomorrow|\.|$)', user_input)
        if match:
            return match.group(1).strip().capitalize()

        # Pattern 2: "add 'buy groceries'" -> "buy groceries"
        match = re.search(r'(?:create|add|make|new)\s+(?:task|a task)\s+[\'"](.+?)[\'"]', user_input)
        if match:
            return match.group(1).strip()

        # Pattern 3: "create task buy groceries" -> "buy groceries"
        match = re.search(r'(?:create|add|make|new)\s+(?:task|a task)\s+(.+?)(?:\s+for\s+tomorrow|\.|$)', user_input)
        if match:
            return match.group(1).strip().capitalize()

        return user_input.strip().capitalize()

    def _extract_task_title_from_command(self, user_input: str) -> Optional[str]:
        """
        Extract task title from commands like 'complete the grocery shopping task' or 'delete task called meeting'.
        """
        import re

        # Pattern 1: "complete the 'buy groceries' task" -> "buy groceries"
        match = re.search(r'(?:complete|finish|done|mark|delete|remove|update|change|edit)\s+(?:the\s+)?[\'"](.+?)[\'"]\s+(?:task|item)', user_input)
        if match:
            return match.group(1).strip()

        # Pattern 2: "complete the buy groceries task" -> "buy groceries"
        match = re.search(r'(?:complete|finish|done|mark|delete|remove|update|change|edit)\s+(?:the\s+)?(.+?)\s+(?:task|item)', user_input)
        if match:
            return match.group(1).strip()

        # Pattern 3: "complete task buy groceries" -> "buy groceries"
        match = re.search(r'(?:complete|finish|done|mark|delete|remove|update|change|edit)\s+(?:task|item)\s+(.+?)(?:\.|$)', user_input)
        if match:
            return match.group(1).strip()

        # Pattern 4: "mark buy groceries as complete" -> "buy groceries"
        match = re.search(r'(?:mark|complete|finish|done)\s+(.+?)\s+as\s+(?:complete|done|finished)', user_input)
        if match:
            return match.group(1).strip()

        # Pattern 5: "delete buy milk" -> "buy milk" (simple command pattern)
        match = re.search(r'(?:delete|remove|complete|finish|done|mark)\s+(.+?)(?:\.|$)', user_input)
        if match:
            return match.group(1).strip()

        return None

    def _find_task_by_title(self, tasks: List[Dict], title: str, user_id: str) -> Optional[Dict]:
        """
        Find a task in the user's task list by title (case-insensitive partial match).
        """
        title_lower = title.lower().strip()
        if not title_lower:
            return None

        # First try exact match (case-insensitive)
        for task in tasks:
            task_title = task.get("title", "").lower().strip()
            if task_title == title_lower:
                return task

        # Try loose matching with fuzzy logic
        for task in tasks:
            task_title = task.get("title", "").lower().strip()

            # Direct inclusion check
            if title_lower in task_title or task_title in title_lower:
                return task

            # Handle common word removal and variations
            simplified_title = title_lower.replace('the ', '').replace('a ', '').strip()
            simplified_task_title = task_title.replace('the ', '').replace('a ', '').strip()

            if simplified_title == simplified_task_title:
                return task
            if simplified_title in simplified_task_title or simplified_task_title in simplified_title:
                return task

        # If still no match, try even looser matching
        for task in tasks:
            task_title = task.get("title", "").lower().strip()

            # Check for word-by-word matching - if most words in the search term exist in task
            title_words = set(title_lower.split())
            task_words = set(task_title.split())

            # If all or most words in the search term are in the task title
            if len(title_words.intersection(task_words)) > 0 and len(title_words) > 0:
                # At least 50% of search words should be in task title
                common_words = title_words.intersection(task_words)
                if len(common_words) / len(title_words) >= 0.5:
                    return task

        return None


# Global instance
agents_integration = OpenAIAgentsIntegration()