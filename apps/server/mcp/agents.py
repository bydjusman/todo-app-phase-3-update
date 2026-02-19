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
        Basic intent recognition and tool execution.
        """
        user_input_lower = user_input.lower()

        # Simple pattern matching for intent recognition
        if any(word in user_input_lower for word in ["create", "add", "new", "make"]):
            # Extract task title (simple extraction)
            title = self._extract_task_title(user_input)
            if title:
                return self.execute_tool("add_task", {"title": title}, user_id)

        elif any(word in user_input_lower for word in ["list", "show", "get", "what", "have"]):
            # Check if asking for completed tasks
            if any(word in user_input_lower for word in ["completed", "done", "finished"]):
                return self.execute_tool("list_tasks", {"status": "completed"}, user_id)
            elif any(word in user_input_lower for word in ["pending", "todo", "not done"]):
                return self.execute_tool("list_tasks", {"status": "pending"}, user_id)
            else:
                return self.execute_tool("list_tasks", {"status": "all"}, user_id)

        elif any(word in user_input_lower for word in ["complete", "finish", "done", "mark"]):
            # This would require more sophisticated parsing to extract task id
            # For now, we'll just return a message
            return {
                "message": "To complete a task, please specify which task you want to mark as completed.",
                "intent": "unknown"
            }

        elif any(word in user_input_lower for word in ["delete", "remove", "cancel"]):
            # This would require more sophisticated parsing to extract task id
            # For now, we'll just return a message
            return {
                "message": "To delete a task, please specify which task you want to remove.",
                "intent": "unknown"
            }

        elif any(word in user_input_lower for word in ["update", "change", "edit", "modify"]):
            # This would require more sophisticated parsing
            return {
                "message": "To update a task, please specify which task and what changes you want to make.",
                "intent": "unknown"
            }

        else:
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


# Global instance
agents_integration = OpenAIAgentsIntegration()