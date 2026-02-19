from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from uuid import uuid4


# Base classes for common fields
class ConversationBase(SQLModel):
    title: Optional[str] = Field(default=None, max_length=200, description="Optional title for the conversation")


class MessageBase(SQLModel):
    role: str = Field(regex="^(user|assistant)$", description="Message role: 'user' or 'assistant'")
    content: str = Field(min_length=1, max_length=10000, description="Message content")
    tool_calls: Optional[str] = Field(default=None, description="JSON string of tool calls made by the assistant")


# Forward reference workaround - define in correct order
class Message(MessageBase, table=True):
    """
    Message model representing a message in a conversation.
    """
    __tablename__ = "messages"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    conversation_id: str = Field(
        description="Foreign key to conversations.id",
        foreign_key="conversations.id",
        sa_column_kwargs={"index": True}
    )
    user_id: str = Field(
        max_length=255,
        description="Foreign key to Better Auth users.id",
        sa_column_kwargs={"index": True}
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp",
        sa_column_kwargs={"index": True}
    )

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a chat conversation.
    """
    __tablename__ = "conversations"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(
        max_length=255,
        description="Foreign key to Better Auth users.id",
        sa_column_kwargs={"index": True}
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Conversation creation timestamp",
        sa_column_kwargs={"index": True}
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Conversation last update timestamp"
    )

    # Relationship to messages
    messages: List[Message] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
        }
    )