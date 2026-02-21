# ADR 001: OpenAI Agents SDK Integration with MCP Tools

## Status
Accepted

## Date
2026-02-21

## Context
We need to implement a chatbot feature that allows users to interact with their todo tasks using natural language. The system must ensure secure, authenticated access to user-specific data while maintaining a clean separation of concerns between the AI processing layer and the business logic layer.

## Decision
We will integrate OpenAI Agents SDK with Model Context Protocol (MCP) tools to create a secure and maintainable architecture that:
- Uses a main chat agent to handle user interactions
- Employs a task operation sub-agent to handle specific task operations
- Routes all database operations through MCP tools only (no direct database access)
- Maintains user authentication and data isolation through the MCP layer

## Alternatives Considered
1. **Direct database access from agents**: Agents would connect directly to the database. This approach was rejected due to security concerns and violation of separation of concerns principles.
2. **Simple function calling approach**: Using basic OpenAI function calling without MCP. This was rejected due to lack of standardization and tool management capabilities that MCP provides.
3. **Custom NLP parser**: Building our own natural language processing instead of using OpenAI Agents. This was rejected due to the complexity and maintenance burden.

## Consequences
### Positive
- Clear separation of AI processing logic from business logic
- Standardized tool interface through MCP protocol
- Enhanced security through centralized access control in MCP tools
- Scalable architecture for adding new agent capabilities

### Negative
- Additional complexity in the agent-to-tool communication layer
- Potential latency introduced by the MCP tool layer
- Dependency on OpenAI's agent platform and MCP protocol

## Implementation Notes
- All database operations must be wrapped in MCP tools
- Authentication tokens (user_id) must be passed from JWT to MCP tools
- The MCP server will validate user access for each operation
- Conversation state management will be handled by OpenAI's agent system