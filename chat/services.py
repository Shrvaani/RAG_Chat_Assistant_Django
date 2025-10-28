from django.conf import settings
from .models import Chat, Message
from services.ai_service import AIService
from services.pinecone_service import PineconeService

class ConversationService:
    """Service for managing conversation context and AI responses"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.pinecone_service = PineconeService()
    
    def get_conversation_context(self, chat_id, limit=10):
        """Get recent conversation history for context"""
        try:
            chat = Chat.objects.get(supabase_id=chat_id)
            messages = Message.objects.filter(chat=chat).order_by('-created_at')[:limit]
            return [{
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at
            } for msg in reversed(messages)]
        except Chat.DoesNotExist:
            return []
    
    def generate_response_with_context(self, message, chat_id, use_rag=True):
        """Generate AI response with conversation context"""
        try:
            # Get conversation history
            conversation_history = self.get_conversation_context(chat_id)
            
            # If RAG is enabled, retrieve relevant documents
            sources = []
            rag_context = ""
            if use_rag:
                try:
                    print(f"RAG: Searching for documents related to: {message}")
                    sources = self.ai_service.retrieve_documents(message, chat_id=chat_id)
                    print(f"RAG: Found {len(sources)} sources")
                    
                    # Debug: Print what we're actually retrieving
                    for i, source in enumerate(sources):
                        print(f"RAG: Source {i+1} content preview: {source.get('text', '')[:200]}...")
                        print(f"RAG: Source {i+1} page: {source.get('page', 'unknown')}")
                        print(f"RAG: Source {i+1} score: {source.get('score', 'unknown')}")
                    
                    # Build context from retrieved documents
                    if sources:
                        rag_context = "\n\nRelevant information from uploaded documents:\n"
                        for i, source in enumerate(sources):
                            text_content = source.get('text', '')
                            print(f"RAG: Source {i+1} text length: {len(text_content)}")
                            if text_content:  # Only add non-empty content
                                rag_context += f"[Source {i+1}]: {text_content}\n"
                        print(f"RAG: Total context length: {len(rag_context)}")
                        print(f"RAG: Context preview: {rag_context[:500]}...")
                    else:
                        print("RAG: No sources found")
                except Exception as e:
                    print(f"RAG retrieval failed: {e}")
                    import traceback
                    traceback.print_exc()
                    sources = []
            
            # Generate AI response with RAG context
            if rag_context:
                # Add RAG context to the conversation
                enhanced_message = f"{message}\n\n{rag_context}"
                print(f"RAG: Enhanced message preview: {enhanced_message[:500]}...")
                response = self.ai_service.generate_response(enhanced_message, conversation_history)
            else:
                print("RAG: No context available, using regular response")
                response = self.ai_service.generate_response(message, conversation_history)
            
            return response, sources
            
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return f"Sorry, I encountered an error while processing your message: {str(e)}", []
    
    def build_context_prompt(self, conversation_history, current_message):
        """Build a context-aware prompt for the AI"""
        if not conversation_history:
            return f"Human: {current_message}\n\nAssistant:"
        
        context = "You are a helpful AI assistant. Here's our conversation so far:\n\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "Human" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        context += f"\nHuman: {current_message}\n\nAssistant:"
        return context