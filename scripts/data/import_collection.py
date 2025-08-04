import os
import internetarchive as ia
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from backend.app.database.connection import SessionLocal
from backend.app.database import models, schemas
from backend.app.services.ia_service import InternetArchiveService
from backend.app.config import settings

# Initialize the Internet Archive service
ia_service = InternetArchiveService()

def import_books_from_collection(db_session: Session, collection_id: str, max_items: int = None):
    """
    Fetches books from a specified Internet Archive collection and imports them into TiDB.
    """
    print(f"--- Starting import from collection: {collection_id} ---")
    
    query = f'collection:({collection_id}) AND mediatype:(texts)'
    # Use max_items for development/testing, or set to None for full collection
    params = {'rows': max_items} if max_items else {}
    items = ia.search_items(query, params=params)
    
    processed_count = 0
    with db_session:
        for item in items:
            ia_id = item['identifier']
            
            # Use a fresh query for each item to avoid stale data
            if db_session.query(models.Book).filter(models.Book.ia_id == ia_id).first():
                print(f"Book with IA ID {ia_id} already exists, skipping.")
                continue
            
            try:
                print(f"Processing book: {ia_id}")
                # Fetch full metadata and content
                metadata = ia_service.get_book_metadata(ia_id)
                content = ia_service.get_book_content(ia_id)
                
                # Transform IA metadata into our internal Pydantic schema
                book_schema = ia_service.create_book_schema_from_ia_metadata(metadata, content)
                
                # Create a new Book model instance
                db_book = models.Book(**book_schema.dict())
                db_session.add(db_book)
                
                processed_count += 1
                
                # Commit periodically for efficiency and to save progress
                if processed_count % 50 == 0:
                    db_session.commit()
                    print(f"Committed batch of 50. Total processed: {processed_count}")
            
            except FileNotFoundError:
                print(f"ERROR: No suitable text file found for book {ia_id}, skipping.")
                db_session.rollback() # Rollback the current item
            except Exception as e:
                print(f"CRITICAL ERROR processing book {ia_id}: {e}")
                db_session.rollback() # Rollback the current item
    
    # Final commit for any remaining items
    db_session.commit()
    print(f"\n--- Import from '{collection_id}' finished! Total new books imported: {processed_count} ---")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        # We will import books from the Gutenberg collection
        # Let's set a smaller max_items for a quick test run. 
        # For full import, set to None.
        import_books_from_collection(db, 'gutenberg', max_items=100)
        
        # We will also import books from the Children's Library collection
        import_books_from_collection(db, 'iacl', max_items=50)

    finally:
        db.close()
