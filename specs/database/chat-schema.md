# Database Schema Specification: Chat Models

## Overview
This specification defines the database schema for the chat functionality, including models for managing conversations and individual messages. The schema follows Phase-3 database model table definitions and supports the stateless chat endpoint requirements.

## Database Entities

### Conversation Table
Stores information about individual chat conversations.

**Table Name**: `conversations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the conversation |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user who owns this conversation |
| title | VARCHAR(255) | NOT NULL | Auto-generated title for the conversation based on first message |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the conversation was last updated |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether the conversation is currently active |

**Indexes**:
- `idx_conversations_user_id`: Index on user_id for fast user-specific queries
- `idx_conversations_created_at`: Index on created_at for chronological sorting
- `idx_conversations_updated_at`: Index on updated_at for recency-based queries

**Constraints**:
- `fk_conversations_user_id`: Foreign key constraint linking to users table
- `chk_conversations_user_id_not_null`: user_id cannot be NULL

### Message Table
Stores individual messages within conversations.

**Table Name**: `messages`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the message |
| conversation_id | UUID | FOREIGN KEY, NOT NULL | Reference to the conversation this message belongs to |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user who sent this message |
| role | VARCHAR(20) | NOT NULL | Message role ('user', 'assistant', 'system') |
| content | TEXT | NOT NULL | The actual message content |
| intent | VARCHAR(50) | | Detected intent from natural language processing |
| entities | JSONB | | Extracted entities in JSON format |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the message was sent |
| tool_calls | JSONB | | Details of any tools called as result of this message |
| tool_responses | JSONB | | Results from tool calls |
| parent_message_id | UUID | FOREIGN KEY | Reference to parent message for threaded conversations |

**Indexes**:
- `idx_messages_conversation_id`: Index on conversation_id for conversation-based queries
- `idx_messages_user_id`: Index on user_id for user-specific queries
- `idx_messages_created_at`: Index on created_at for chronological sorting
- `idx_messages_intent`: Index on intent for intent-based analytics

**Constraints**:
- `fk_messages_conversation_id`: Foreign key constraint linking to conversations table
- `fk_messages_user_id`: Foreign key constraint linking to users table
- `fk_messages_parent_message_id`: Foreign key constraint linking to messages table (self-reference)
- `chk_messages_role_valid`: role must be one of ('user', 'assistant', 'system')
- `chk_messages_content_not_empty`: content cannot be empty or only whitespace

## Relationships
- `conversations.user_id` → `users.id` (one-to-many)
- `messages.conversation_id` → `conversations.id` (many-to-one)
- `messages.user_id` → `users.id` (many-to-one)
- `messages.parent_message_id` → `messages.id` (self-referencing, optional)

## Data Retention Policy
- Messages: Retain for 2 years from creation date
- Conversation metadata: Retain for 3 years from last activity
- Automatic cleanup jobs will run monthly to remove expired data

## Indexing Strategy
- Primary indexes on foreign key relationships to optimize joins
- Time-based indexes for chronological queries
- Specific indexes for frequently queried columns (intent, role)

## Performance Considerations
- Use UUIDs for distributed systems compatibility
- JSONB for flexible entity and parameter storage
- Proper indexing to support conversation timeline queries
- Consider partitioning by user_id or created_at for large-scale deployments

## Security & Privacy
- All user data must be encrypted at rest
- Sensitive PII should be masked or anonymized where possible
- Proper access controls based on user_id for data isolation
- Audit trail for all data access and modifications

## Success Criteria
- Schema supports all required chat functionality
- Query performance meets response time requirements
- Data integrity constraints prevent invalid states
- Privacy and security requirements are met