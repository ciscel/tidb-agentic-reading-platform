import internetarchive as ia
from typing import Dict, Any, Optional
from backend.app.database import schemas

class InternetArchiveService:
    """
    Service class for interacting with the Internet Archive API.
    """
    def __init__(self):
        # We can perform any client initialization here if needed.
        pass

    def get_book_metadata(self, ia_id: str) -> Dict[str, Any]:
        """
        Fetches the full metadata for a given Internet Archive item ID.
        """
        try:
            item = ia.get_item(ia_id)
            return item.metadata
        except Exception as e:
            print(f"Error fetching metadata for {ia_id}: {e}")
            return {}

    def get_book_content(self, ia_id: str) -> str:
        """
        Fetches the text content of a book from the Internet Archive.
        Prioritizes the `text` file format.
        """
        try:
            item = ia.get_item(ia_id)
            text_file = item.get_file(f"{ia_id}.txt")
            if text_file:
                return text_file.download().decode('utf-8')
            
            # If no .txt file, try to find a suitable text-like file
            for file in item.files:
                if file['name'].endswith('.txt'):
                    return item.get_file(file['name']).download().decode('utf-8')
                    
            raise FileNotFoundError(f"No suitable text file found for {ia_id}")
            
        except Exception as e:
            print(f"Error fetching content for {ia_id}: {e}")
            raise

    def create_book_schema_from_ia_metadata(self, metadata: Dict[str, Any], content: str) -> schemas.BookCreate:
        """
        Transforms raw Internet Archive metadata into our Pydantic BookCreate schema.
        """
        ia_id = metadata.get('identifier', 'unknown')
        title = metadata.get('title', 'Unknown Title')
        
        # Internet Archive authors can be a string or a list, so we handle both.
        author = metadata.get('creator')
        if isinstance(author, list):
            author = ", ".join(author)
        
        # Use Pydantic's data validation to handle the rest
        return schemas.BookCreate(
            ia_id=ia_id,
            title=title,
            author=author,
            language=metadata.get('language'),
            description=metadata.get('description'),
            cover_image_url=metadata.get('boxid'), # 'boxid' is a good proxy for an image identifier
            content=content
        )
