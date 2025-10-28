from django.conf import settings
from pinecone import Pinecone

class PineconeService:
    """Service for Pinecone vector database operations"""
    
    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        self.pc = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize Pinecone index"""
        try:
            if not self.api_key or not self.index_name:
                print("Pinecone credentials not configured")
                self.index = None
                return
            # Use new Pinecone API
            self.pc = Pinecone(api_key=self.api_key)
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Pinecone initialization failed: {e}")
            self.index = None
    
    def upsert_vectors(self, vectors):
        """Upsert vectors to Pinecone"""
        if not self.index:
            return False
        try:
            self.index.upsert(vectors=vectors)
            return True
        except Exception as e:
            print(f"Pinecone upsert failed: {e}")
            return False
    
    def query_vectors(self, query_vector, top_k=5):
        """Query vectors from Pinecone"""
        if not self.index:
            return []
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )
            return results.matches
        except Exception as e:
            print(f"Pinecone query failed: {e}")
            return []
    
    def delete_vectors(self, ids):
        """Delete vectors from Pinecone"""
        if not self.index:
            return False
        try:
            self.index.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Pinecone delete failed: {e}")
            return False
    
    def clear_old_vectors(self, chat_id):
        """Clear old vectors for a specific chat to avoid stale data"""
        if not self.index:
            return False
        try:
            # Delete all vectors for this chat
            self.index.delete(filter={"chat_id": chat_id})
            print(f"Cleared old vectors for chat: {chat_id}")
            return True
        except Exception as e:
            print(f"Failed to clear old vectors: {e}")
            return False