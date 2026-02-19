# Architecture Specification: AI Chatbot System

## Overview
This document defines the architectural approach for implementing an AI chatbot that enables natural language interaction with the todo management system. The architecture leverages ChatKit for the frontend, FastAPI for the backend, OpenAI Agents SDK, MCP server, and Neon PostgreSQL database in a stateless design pattern.

## System Context
The AI chatbot system integrates with the existing monorepo architecture, providing a conversational interface for task management through natural language processing capabilities.

### External Dependencies
- OpenAI API for language processing and agent capabilities
- MCP (Model Context Protocol) for standardized tool integration
- Better Auth for JWT-based authentication
- Neon PostgreSQL for managed database services
- ChatKit for frontend chat UI components

## Architecture Layers

### 1. Presentation Layer (ChatKit Frontend)
- **Technology**: ChatKit library with React components
- **Components**:
  - Chat interface with message history display
  - Natural language input field with auto-suggest
  - Response formatting for different message types
  - Loading indicators for processing states
- **Features**:
  - Real-time chat interface with message streaming
  - Typing indicators during AI processing
  - Error handling and user feedback displays
  - Responsive design for multiple device types
- **Integration**:
  - Communicates with FastAPI backend via REST API
  - Handles JWT authentication tokens from Better Auth
  - Manages client-side state for conversation context

### 2. API Gateway Layer (FastAPI Chat Endpoint)
- **Technology**: FastAPI framework for high-performance API
- **Endpoint**: POST /api/{user_id}/chat for stateless requests
- **Features**:
  - Request validation and sanitization
  - JWT authentication middleware using Better Auth
  - Rate limiting to prevent abuse
  - Request/response logging and monitoring
  - Error handling with appropriate HTTP status codes
- **Middleware**:
  - Authentication validation
  - Request/response logging
  - CORS configuration for frontend access
  - Response compression for performance

### 3. Application Logic Layer (OpenAI Agents SDK)
- **Technology**: OpenAI Agents SDK for structured AI interactions
- **Components**:
  - Agent instance with specific instructions for task management
  - Tool calling mechanism for executing backend operations
  - Memory management for conversation context
  - Response formatting for user-friendly output
- **Features**:
  - Intent recognition from natural language input
  - Entity extraction for task parameters
  - Tool selection based on detected intent
  - Conversation state management with context tracking

### 4. MCP Integration Layer (MCP Server)
- **Technology**: Model Context Protocol server implementation
- **Components**:
  - Tool registration system for available operations
  - Tool calling interface for OpenAI Agents SDK
  - Authentication forwarding for user validation
  - Request/response formatting between layers
- **Tools Available**:
  - `@tools/add_task`: Create new tasks via natural language
  - `@tools/list_tasks`: Retrieve tasks with filtering options
  - `@tools/complete_task`: Mark tasks as completed
  - `@tools/delete_task`: Delete specific tasks with confirmation
  - `@tools/update_task`: Update task properties
- **Features**:
  - Standardized tool interfaces following MCP protocol
  - Authentication validation for each tool call
  - Error handling and response formatting
  - Logging for audit and debugging purposes

### 5. Backend Service Layer
- **Technology**: Python services integrated with FastAPI
- **Components**:
  - Task management services for CRUD operations
  - User management services for authentication validation
  - Conversation management services for chat persistence
  - Operation logging services for audit and analytics
- **Features**:
  - Business logic validation for task operations
  - User authorization checks for task access
  - Integration with database layer for data persistence
  - Error handling and response formatting

### 6. Data Layer (Neon PostgreSQL)
- **Technology**: Neon PostgreSQL managed database service
- **Components**:
  - Conversation table for storing chat session metadata
  - Message table for individual chat messages
  - Connection pooling for optimal performance
  - Automated backup and scaling capabilities
- **Features**:
  - ACID compliance for data integrity
  - JSONB support for flexible entity storage
  - Built-in connection pooling and scaling
  - Point-in-time recovery for data protection

## Stateless Request Cycle

The architecture follows a completely stateless design where each request contains all necessary context:

### 1. Client Request
- User enters natural language command in ChatKit interface
- Client validates input and adds authentication token
- Request is sent to POST /api/{user_id}/chat endpoint

### 2. Authentication & Validation
- FastAPI endpoint validates JWT token from Better Auth
- Request body is validated against defined schema
- User authorization is confirmed for requested operations

### 3. OpenAI Agent Processing
- Request is passed to OpenAI Agents SDK
- Agent processes natural language to identify intent
- Relevant entities are extracted from the user input
- Appropriate MCP tools are selected based on intent

### 4. MCP Tool Execution
- MCP server receives tool call with parameters
- Authentication is validated for each tool execution
- Backend service layer is invoked with proper context
- Tool response is formatted and returned to agent

### 5. Response Generation
- OpenAI agent formats response based on tool results
- Response includes user-friendly message and action confirmation
- Additional context information is included as needed

### 6. Client Response
- FastAPI endpoint returns response to client
- ChatKit frontend displays response to user
- Conversation state is updated in client interface

## Tool Execution Flow

The tool execution follows a standardized flow through the MCP protocol:

### Tool Request Flow
1. **Intent Detection**: User message → OpenAI Agent → Intent identification
2. **Tool Selection**: Intent → MCP tool mapping → Tool selection
3. **Parameter Extraction**: Entities from message → Tool parameters
4. **Authentication Check**: User validation → MCP server → Authorization
5. **Tool Execution**: MCP server → Backend service → Database operation
6. **Result Formatting**: Backend response → MCP response → Agent response
7. **User Response**: Formatted response → ChatKit frontend → User display

### Example Flow for "Add Task"
```
User: "Create a task to buy groceries tomorrow"
1. Intent detected: create_task
2. Tool selected: @tools/add_task
3. Parameters extracted: {title: "buy groceries", due_date: "tomorrow", user_id: "user-123"}
4. Authentication validated for user-123
5. add_task tool executes → Creates task in database
6. Response formatted: {task_id: "task-456", title: "buy groceries", status: "pending"}
7. User receives: "I've created the task 'buy groceries' for tomorrow."
```

## Technology Stack

### Frontend Technologies
- **Framework**: React with Next.js for server-side rendering
- **UI Library**: ChatKit for chat interface components
- **Authentication**: Better Auth for JWT token management
- **State Management**: Built-in React hooks for client-side state

### Backend Technologies
- **Framework**: FastAPI for high-performance API development
- **AI/ML**: OpenAI Agents SDK for structured AI interactions
- **Protocol**: MCP (Model Context Protocol) for standardized tool integration
- **Database**: Neon PostgreSQL for managed database services
- **Authentication**: Better Auth for JWT validation middleware

### Infrastructure
- **Hosting**: Vercel for frontend deployment with serverless functions
- **Database**: Neon PostgreSQL for managed database hosting
- **AI Service**: OpenAI API for language processing
- **Monitoring**: Built-in logging and metrics collection

## Security Architecture
- End-to-end authentication with JWT token validation at FastAPI layer
- Input sanitization and validation at API gateway
- Secure communication between all service layers
- Proper isolation of user data through user_id validation
- Audit trails for all user actions through MCP logging
- Encrypted data at rest with Neon PostgreSQL security features

## Performance Considerations
- FastAPI's async capabilities for handling concurrent requests
- Neon PostgreSQL connection pooling for database efficiency
- OpenAI Agent's optimized tool calling for minimal latency
- ChatKit's efficient rendering for responsive UI
- CDN delivery for static assets and optimized client delivery

## Scalability Strategy
- Horizontal scaling of FastAPI serverless functions
- Neon PostgreSQL's auto-scaling capabilities for database load
- OpenAI API's inherent scalability for AI processing
- Stateless architecture enabling infinite request scaling
- Caching layer potential for frequently accessed data

## Monitoring & Observability
- Request/response logging with correlation IDs across all components
- Performance metrics for response times and error rates
- MCP tool usage analytics for system optimization
- User engagement metrics for chatbot effectiveness
- System health monitoring for all architectural components
- Alerting for service degradation or failures

## Data Flow Architecture
- Natural language input → ChatKit frontend → FastAPI endpoint → OpenAI Agent → MCP tools → Backend services → Neon PostgreSQL
- All interactions logged for analytics and debugging
- User data isolated by authentication and authorization at each layer
- Stateless design ensures no server-side session dependencies

## Success Criteria
- Architecture supports all required chatbot functionality with high performance
- System handles expected load with appropriate response time characteristics
- Security requirements are met at all architectural layers
- Scalability requirements are addressed in the design
- Integration with existing systems is seamless
- Stateless architecture provides reliable, scalable performance