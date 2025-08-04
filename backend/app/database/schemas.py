from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    ia_id: str
    title: str
    author: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    content: str

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        orm_mode = True # Enables the Pydantic model to work with ORM objects


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ReadingSessionBase(BaseModel):
    user_id: int
    book_id: int
    progress: int
    last_page: int
    last_access: datetime

class ReadingSession(ReadingSessionBase):
    id: int

    class Config:
        orm_mode = True

