# Services package initialization
# Note: Services are instantiated directly where needed, not at module level
# to avoid startup errors if credentials are not configured
from .pinecone_service import PineconeService
from .ai_service import AIService

__all__ = ['PineconeService', 'AIService']
