# Services package initialization
from .supabase_service import SupabaseService
from .pinecone_service import PineconeService
from .ai_service import AIService

# Initialize services
supabase_service = SupabaseService()
pinecone_service = PineconeService()
ai_service = AIService()
