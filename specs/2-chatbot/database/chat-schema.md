# Database Schema Specification: Chatbot

## Overview
This specification defines the database schema requirements for the AI chatbot feature, including conversation history, user interactions, and any additional data needed to support natural language processing and task management operations.

## Database Entities

### ChatSession Table
Stores information about individual chat sessions.

**Table Name**: `chat_sessions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the session |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the session was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the session was last updated |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether the session is currently active |

**Indexes**:
- `idx_chat_sessions_user_id`: Index on user_id for fast user-specific queries
- `idx_chat_sessions_created_at`: Index on created_at for chronological sorting

### ChatMessage Table
Stores individual messages in a chat conversation.

**Table Name**: `chat_messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the message |
| session_id | UUID | FOREIGN KEY, NOT NULL | Reference to the chat session |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user who sent the message |
| role | VARCHAR(20) | NOT NULL | Message role ('user', 'assistant') |
| content | TEXT | NOT NULL | The actual message content |
| intent | VARCHAR(50) | | Detected intent from natural language processing |
| entities | JSONB | | Extracted entities in JSON format |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the message was sent |
| tool_calls | JSONB | | Details of any tools called as result of this message |
| tool_responses | JSONB | | Results from tool calls |

**Indexes**:
- `idx_chat_messages_session_id`: Index on session_id for session-based queries
- `idx_chat_messages_user_id`: Index on user_id for user-specific queries
- `idx_chat_messages_created_at`: Index on created_at for chronological sorting
- `idx_chat_messages_intent`: Index on intent for intent-based analytics

### TaskOperationLog Table
Tracks all task operations performed through the chatbot for audit and analytics.

**Table Name**: `task_operation_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the log entry |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user who initiated the operation |
| session_id | UUID | FOREIGN KEY | Reference to the chat session |
| message_id | UUID | FOREIGN KEY | Reference to the originating chat message |
| operation_type | VARCHAR(20) | NOT NULL | Type of operation ('create', 'read', 'update', 'delete') |
| task_id | UUID | FOREIGN KEY | Reference to the affected task |
| original_command | TEXT | NOT NULL | Original user command that triggered the operation |
| extracted_parameters | JSONB | | Parameters extracted from the command |
| operation_result | JSONB | | Result of the operation |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the operation was logged |

**Indexes**:
- `idx_task_operation_logs_user_id`: Index on user_id for user-specific queries
- `idx_task_operation_logs_task_id`: Index on task_id for task-specific queries
- `idx_task_operation_logs_operation_type`: Index on operation_type for analytics
- `idx_task_operation_logs_created_at`: Index on created_at for chronological sorting

## Relationships
- `chat_sessions.user_id` → `users.id` (one-to-many)
- `chat_messages.session_id` → `chat_sessions.id` (many-to-one)
- `chat_messages.user_id` → `users.id` (many-to-one)
- `task_operation_logs.user_id` → `users.id` (many-to-one)
- `task_operation_logs.session_id` → `chat_sessions.id` (many-to-one)
- `task_operation_logs.message_id` → `chat_messages.id` (many-to-one)
- `task_operation_logs.task_id` → `tasks.id` (many-to-one)

## Data Retention Policy
- Chat messages: Retain for 1 year from creation date
- Session data: Retain for 1 year from last activity
- Operation logs: Retain for 2 years for audit purposes

## Indexing Strategy
- Primary indexes on foreign key relationships to optimize joins
- Time-based indexes for chronological queries
- Specific indexes for frequently queried columns (intent, operation_type)

## Performance Considerations
- Use UUIDs for distributed systems compatibility
- JSONB for flexible entity and parameter storage
- Proper indexing to support conversation timeline queries
- Partitioning consideration for large-scale deployments

## Security & Privacy
- All user data must be encrypted at rest
- Sensitive PII should be masked or anonymized where possible
- Proper access controls based on user_id for data isolation
- Audit trail for all data access and modifications

## Success Criteria
- Schema supports all required chatbot functionality
- Query performance meets response time requirements
- Data integrity constraints prevent invalid states
- Privacy and security requirements are met