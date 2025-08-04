from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.connection import Base

class User(Base):
    """
    Represents a user of the platform.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reading_sessions = relationship("ReadingSession", back_populates="user")


class Book(Base):
    """
    Represents a book ingested from a source like Internet Archive.
    """
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    ia_id = Column(String(255), unique=True, index=True, nullable=False)
    title = Column(String(512), index=True, nullable=False)
    author = Column(String(512), index=True, nullable=True)
    language = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(1024), nullable=True)
    content = Column(Text, nullable=False) # The full text content of the book

    # Relationships
    reading_sessions = relationship("ReadingSession", back_populates="book")

class ReadingSession(Base):
    """
    Tracks a user's reading progress on a specific book.
    """
    __tablename__ = "reading_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    progress = Column(Integer, default=0)  # Percentage read (0-100)
    last_page = Column(Integer, default=0)
    last_access = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reading_sessions")
    book = relationship("Book", back_populates="reading_sessions")
