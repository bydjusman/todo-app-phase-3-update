from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlmodel import Session, select
from models.models import Message, Conversation
from models.task import TaskCreate, TaskUpdate
from auth.jwt import get_current_user, TokenData
from database.session import get_db
from mcp.agents import agents_integration
import uuid
from datetime import datetime, timezone


# Create the API router
router = APIRouter()


@router.post("/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    message: str,
    timestamp: Optional[str] = None,
    context: Optional[dict] = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stateless chat endpoint that processes natural language input and returns appropriate response.
    """
    # Validate that the authenticated user matches the user_id in the path
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's chat"
        )

    # Create or get conversation ID from context or create new
    conversation_id = None
    if context and context.get("session_id"):
        conversation_id = context["session_id"]
    else:
        conversation_id = str(uuid.uuid4())

    # Create conversation if it doesn't exist
    conversation = db.get(Conversation, conversation_id)
    if not conversation:
        # Create a default title based on the first message if available
        title = f"Chat: {message[:50]}..." if len(message) > 50 else f"Chat: {message}"
        conversation = Conversation(
            id=conversation_id,
            title=title,
            user_id=user_id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Create user message record
    user_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=message,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Process the conversation using the agents integration
    try:
        result = agents_integration.process_conversation(
            user_input=message,
            user_id=user_id,
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )

    # Get the intent from the result to determine response
    intent = result.get("intent", "unknown")

    # Create AI response message record
    ai_response_content = result.get("message", f"I processed your request: {message}")
    # Convert the result to a JSON string for tool_calls field
    import json
    tool_calls_str = json.dumps(result) if result else None
    ai_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,  # AI messages are associated with the user's conversation
        role="assistant",
        content=ai_response_content,
        tool_calls=tool_calls_str
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.now(timezone.utc)
    db.add(conversation)
    db.commit()

    # Format the response according to the specification
    response = {
        "id": str(ai_message.id),
        "message": ai_response_content,
        "intent": intent,
        "entities": result.get("entities", {}),
        "action_result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "session_id": conversation_id
        }
    }

    return response


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all conversations for the specified user.
    """
    # Validate that the authenticated user matches the user_id in the path
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's conversations"
        )

    # Query conversations for the user
    conversations = db.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            } for conv in conversations
        ]
    }


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def list_messages(
    user_id: str,
    conversation_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all messages in a specific conversation.
    """
    # Validate that the authenticated user matches the user_id in the path
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's messages"
        )

    # Verify that the conversation belongs to the user
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or not authorized"
        )

    # Query messages for the conversation
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    # Import json to handle tool_calls
    import json
    message_list = []
    for msg in messages:
        # Parse the tool_calls field as JSON
        tool_calls = None
        if msg.tool_calls:
            try:
                tool_calls = json.loads(msg.tool_calls)
            except json.JSONDecodeError:
                tool_calls = msg.tool_calls
        message_list.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        })

    return {
        "messages": message_list
    }