"""
Initialize the database by creating all tables.
Run this script once to set up the database schema.
"""
from sqlmodel import SQLModel
from database.session import engine
from models.task import Task
from models.user import User
from models.models import Conversation, Message


def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
