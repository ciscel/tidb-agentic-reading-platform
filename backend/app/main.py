# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import os
import asyncio

# The name of the LLM to use for generation
# You can use gemini-2.5-flash-preview-05-20 for text generation.
LLM_MODEL = "gemini-2.5-flash-preview-05-20"

# --- API Key Configuration ---
# The API key should be stored securely, e.g., in environment variables.
# For this example, we'll assume it's available.
# In a real-world scenario, never hardcode this.
API_KEY = os.getenv("API_KEY", "")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{LLM_MODEL}:generateContent?key={API_KEY}"

# --- Data Models (Pydantic) ---
class Book(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str] = None
    coverUrl: Optional[str] = None

class BookInsight(BaseModel):
    insight: Optional[str] = None

# --- In-Memory Database (for demonstration) ---
# In a production environment, this would be a real database like TiDB.
BOOKS_DB: Dict[str, dict] = {
    "book-001": {
        "id": "book-001",
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "description": "A comedic science fiction series created by Douglas Adams. Originally a radio comedy broadcast on BBC Radio 4 in 1978, it was later adapted to other formats, including novels, a TV series, a computer game, and a feature film.",
        "coverUrl": "https://placehold.co/100x150/5C6BC0/FFFFFF?text=Book+1"
    },
    "book-002": {
        "id": "book-002",
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "description": "An epic high-fantasy novel by the English author and scholar J. R. R. Tolkien. Set in Middle-earth, the story began as a sequel to Tolkien's 1937 fantasy novel The Hobbit, but eventually developed into a much larger work.",
        "coverUrl": "https://placehold.co/100x150/546E7A/FFFFFF?text=Book+2"
    },
    "book-003": {
        "id": "book-003",
        "title": "Dune",
        "author": "Frank Herbert",
        "description": "A 1965 science fiction novel by American author Frank Herbert, originally published as two separate serials in the magazine Analog. It is the first installment of the Dune saga and is widely considered one of the greatest science fiction novels of all time.",
        "coverUrl": "https://placehold.co/100x150/757575/FFFFFF?text=Book+3"
    }
}

# --- Insight Cache ---
# Cache to store generated insights to avoid re-generating.
# In a real app, this would be part of your database.
INSIGHT_CACHE: Dict[str, str] = {}

# --- FastAPI App Initialization ---
app = FastAPI()

# --- LLM API Call Function with Exponential Backoff ---
async def generate_insight_with_backoff(prompt: str) -> Optional[str]:
    """
    Generates an insight using the LLM with exponential backoff for retries.
    """
    retries = 0
    max_retries = 5
    base_delay = 1.0

    async with httpx.AsyncClient() as client:
        while retries < max_retries:
            try:
                chat_history = [{"role": "user", "parts": [{"text": prompt}]}]
                payload = {"contents": chat_history}
                response = await client.post(API_URL, json=payload)
                response.raise_for_status()

                result = response.json()
                if result.get("candidates"):
                    return result["candidates"][0]["content"]["parts"][0]["text"]
            except httpx.HTTPStatusError as e:
                # Handle throttling (429) or other server errors
                if e.response.status_code == 429 and retries < max_retries - 1:
                    delay = base_delay * (2 ** retries)
                    await asyncio.sleep(delay)
                    retries += 1
                else:
                    raise e
            except Exception as e:
                raise e
    return None

# --- API Endpoints ---
@app.get("/books", response_model=List[Book])
async def get_books():
    """
    Returns a list of all books in the library.
    """
    return [Book(**book) for book in BOOKS_DB.values()]

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    """
    Returns a single book's details. Does not include AI insight.
    """
    book = BOOKS_DB.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(**book)

@app.get("/books/{book_id}/insight", response_model=BookInsight)
async def get_book_insight(book_id: str):
    """
    Returns an AI-generated insight for a book.
    This endpoint is for premium users only.
    """
    # For demonstration, we'll hardcode this, but in a real app, you would
    # check the user's authentication token and subscription status here.
    is_premium_user = True
    
    if not is_premium_user:
        raise HTTPException(status_code=403, detail="Access denied. This feature requires a premium subscription.")

    book_data = BOOKS_DB.get(book_id)
    if not book_data:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book = Book(**book_data)

    # Check if insight is in cache
    if book_id in INSIGHT_CACHE:
        return BookInsight(insight=INSIGHT_CACHE[book_id])

    # If not in cache, generate a new insight
    prompt = f"Provide a 300-word insight for the book '{book.title}' by {book.author}. The book's description is: '{book.description}'. Focus on the main themes and significance."
    try:
        insight_text = await generate_insight_with_backoff(prompt)
        if insight_text:
            INSIGHT_CACHE[book_id] = insight_text  # Cache the result
            return BookInsight(insight=insight_text)
        else:
            raise HTTPException(status_code=500, detail="Failed to generate AI insight.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
