# API Specification: Stateless Chat Endpoint

## Overview
This specification defines the stateless API endpoint for the AI chatbot feature that processes natural language inputs and interacts with the todo management system. The endpoint uses JWT authentication via Better Auth and is designed to be stateless with each request containing all necessary context.

## Endpoint Definition

### POST /api/{user_id}/chat
Processes natural language input from the user and returns the appropriate response for the specific user's context.

**Endpoint Parameters**:
- `user_id` (path parameter): The unique identifier of the authenticated user

#### Request
**Method**: POST
**Path**: /api/{user_id}/chat
**Content-Type**: application/json

**Request Headers**:
- `Authorization: Bearer {jwt_token}` - JWT authentication token from Better Auth
- `Content-Type: application/json`

**Request Schema**:
```json
{
  "type": "object",
  "properties": {
    "message": {
      "type": "string",
      "description": "Natural language command from user",
      "minLength": 1,
      "maxLength": 1000
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of the request",
      "default": "current timestamp"
    },
    "context": {
      "type": "object",
      "description": "Optional context information for this request",
      "properties": {
        "session_id": {
          "type": "string",
          "description": "Optional session identifier for context tracking"
        },
        "previous_messages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "role": {
                "type": "string",
                "enum": ["user", "assistant"]
              },
              "content": {
                "type": "string"
              }
            }
          },
          "maxItems": 10,
          "description": "Previous conversation messages to provide context (stateless alternative)"
        }
      }
    }
  },
  "required": ["message"],
  "additionalProperties": false
}
```

**Example Request Body**:
```json
{
  "message": "Create a task to buy groceries tomorrow",
  "timestamp": "2026-02-19T15:30:00Z",
  "context": {
    "session_id": "session-123",
    "previous_messages": [
      {
        "role": "user",
        "content": "I need to buy groceries"
      },
      {
        "role": "assistant",
        "content": "I've created a task for buying groceries."
      }
    ]
  }
}
```

#### Response
**Success Response (200 OK)**:
```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Response identifier"
    },
    "message": {
      "type": "string",
      "description": "Response to the user"
    },
    "intent": {
      "type": "string",
      "enum": ["create_task", "list_tasks", "complete_task", "delete_task", "update_task", "unknown"],
      "description": "Detected intent from natural language processing"
    },
    "entities": {
      "type": "object",
      "description": "Extracted entities from the user's message",
      "properties": {
        "task_title": {
          "type": "string",
          "description": "Extracted task title if applicable"
        },
        "due_date": {
          "type": "string",
          "format": "date-time",
          "description": "Extracted due date in ISO 8601 if applicable"
        },
        "task_id": {
          "type": "string",
          "description": "ID of specific task if referenced"
        },
        "status_filter": {
          "type": "string",
          "enum": ["all", "pending", "completed", "overdue"],
          "description": "Status filter if applicable"
        },
        "priority": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "description": "Priority level if specified"
        }
      }
    },
    "action_result": {
      "type": "object",
      "description": "Result of the action performed if any"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of response"
    },
    "context": {
      "type": "object",
      "description": "Context information for conversation flow",
      "properties": {
        "session_id": {
          "type": "string",
          "description": "Session identifier"
        }
      }
    }
  },
  "required": ["id", "message", "intent", "timestamp"],
  "additionalProperties": false
}
```

**Example Success Response**:
```json
{
  "id": "resp-789",
  "message": "I've created the task 'buy groceries' for tomorrow.",
  "intent": "create_task",
  "entities": {
    "task_title": "buy groceries",
    "due_date": "2026-02-20T00:00:00Z"
  },
  "action_result": {
    "task_id": "task-456",
    "title": "buy groceries",
    "status": "pending"
  },
  "timestamp": "2026-02-19T15:30:15Z",
  "context": {
    "session_id": "session-123"
  }
}
```

#### Error Responses

**Authentication Error (401 Unauthorized)**:
```json
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED",
  "message": "Valid JWT token required for access"
}
```

**Forbidden Error (403 Forbidden)**:
```json
{
  "error": "Access forbidden",
  "code": "FORBIDDEN",
  "message": "You are not authorized to access this user's chat"
}
```

**Bad Request (400 Bad Request)**:
```json
{
  "error": "Invalid request format",
  "code": "INVALID_INPUT",
  "message": "Request body does not match schema",
  "details": {
    "field": "message",
    "reason": "Message is required and must be a string"
  }
}
```

**Not Found (404 Not Found)**:
```json
{
  "error": "User not found",
  "code": "USER_NOT_FOUND",
  "message": "The specified user ID does not exist"
}
```

**Server Error (500 Internal Server Error)**:
```json
{
  "error": "Internal server error",
  "code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred during processing"
}
```

## Authentication & Authorization

### JWT (Better Auth) Validation
- All requests must include a valid JWT token in the Authorization header
- Token must contain valid user identity information
- The user_id in the token must match the user_id in the path parameter
- Better Auth will validate the token signature and expiration

### User Permissions
- Users can only access their own chat endpoint (user_id in JWT must match user_id in path)
- System will validate that any task-specific operations are authorized for the requesting user

## Stateless Flow Steps

The endpoint follows a completely stateless architecture where each request contains all necessary information:

### 1. Request Reception
- Client sends POST request to `/api/{user_id}/chat`
- Request includes JWT token in Authorization header
- Request body contains natural language message and optional context

### 2. Authentication Validation
- Verify JWT token using Better Auth middleware
- Validate that user_id in token matches user_id in path parameter
- Return 401/403 if authentication fails

### 3. Request Validation
- Validate request body against schema
- Return 400 if validation fails

### 4. Natural Language Processing
- Pass user message to NLP system for intent recognition
- Extract entities from the message (task title, due date, etc.)

### 5. Context Enrichment (Optional)
- If context is provided in request, use it for disambiguation
- If previous_messages are provided, use them for reference resolution
- Do NOT store or retrieve any server-side context

### 6. MCP Tool Selection
- Based on detected intent, select appropriate MCP tool to call
- Pass extracted entities as parameters to the MCP tool
- Include user_id for authorization validation

### 7. MCP Tool Execution
- Execute selected MCP tool with provided parameters
- Tools handle authorization and business logic
- Return results to chat endpoint

### 8. Response Formatting
- Format tool results into user-friendly response
- Include original intent and extracted entities in response
- Add timestamp and response ID

### 9. Response Transmission
- Return formatted response to client
- No session state stored on server

## Performance Requirements
- 95% of requests should respond within 2 seconds
- Endpoint should handle at least 100 concurrent connections
- Proper caching where appropriate for repeated requests

## Security Considerations
- Input sanitization to prevent injection attacks
- Proper validation of all request parameters
- Secure handling of user-specific data
- Token expiration validation

## Error Handling
- Invalid natural language inputs should return helpful suggestions
- System errors should be logged but not expose internal details to users
- Network timeouts should return appropriate error messages
- Validation errors should include specific field details

## Success Criteria
- API responds to 95% of valid requests within 2 seconds
- 99.9% uptime during business hours
- Proper error handling for 100% of edge cases
- Complete authentication validation for all requests