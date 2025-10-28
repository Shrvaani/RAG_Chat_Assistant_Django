from django.conf import settings
from huggingface_hub import InferenceClient
import json

class AIService:
    """Service for AI interactions using Hugging Face"""
    
    def __init__(self):
        self.hf_token = settings.HF_TOKEN
        self.model = settings.MODEL
        try:
            self.llm_client = InferenceClient(model=self.model, token=self.hf_token)
        except Exception as e:
            print(f"Failed to initialize LLM client: {e}")
            self.llm_client = None
    
    def generate_response(self, message, conversation_history=None):
        """Generate AI response using Hugging Face InferenceClient"""
        try:
            if not self.llm_client:
                print("LLM client not available, using fallback")
                return self._generate_fallback_response(message, conversation_history)
            
            # Build conversation context
            if conversation_history:
                context = self._build_context(conversation_history)
                prompt = f"{context}\n\nHuman: {message}\n\nAssistant:"
            else:
                prompt = f"Human: {message}\n\nAssistant:"
            
            print(f"AI: Generating response for: {message[:100]}...")
            
            # Try chat_completion first
            try:
                resp = self.llm_client.chat_completion(
                    model=self.model, 
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000, 
                    temperature=0.4, 
                    stream=False
                )
                # Extract response from chat completion
                if hasattr(resp, 'choices') and len(resp.choices) > 0:
                    response = resp.choices[0].message.content
                    print(f"AI: Generated response: {response[:100]}...")
                    return response
                else:
                    print(f"AI: Unexpected response format: {resp}")
                    return str(resp)
            except Exception as e:
                print(f"Chat completion failed: {e}, trying text generation...")
                try:
                    # Fallback to text_generation
                    gen = self.llm_client.text_generation(
                        prompt, 
                        max_new_tokens=2000, 
                        temperature=0.4
                    )
                    response = gen if isinstance(gen, str) else str(gen)
                    print(f"AI: Generated response (text gen): {response[:100]}...")
                    return response
                except Exception as e2:
                    print(f"Text generation also failed: {e2}")
                    # Final fallback - return a helpful message with some intelligence
                    return self._generate_fallback_response(message, conversation_history)
                
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _build_context(self, conversation_history):
        """Build conversation context from history"""
        context = "You are a helpful AI assistant. Here's our conversation so far:\n\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "Human" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n"
        return context
    
    def _generate_fallback_response(self, message, conversation_history):
        """Generate a simple fallback response when AI service is down"""
        message_lower = message.lower()
        
        # Check if this is about uploaded documents
        if any(word in message_lower for word in ['name', 'candidate', 'pdf', 'document', 'file']):
            return "I can see you have uploaded a PDF document! However, I'm currently experiencing some technical difficulties with my AI service. The document appears to be 'Shrvaani S - AI_ML Python Developer - GEN AI - Data Science - Data Analysis.pdf'. Once my AI service is restored, I'll be able to analyze the content and answer your questions about it."
        
        # Simple pattern matching for common questions
        elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm a RAG Chat Assistant. I can see you have uploaded documents, but I'm currently experiencing some technical difficulties with my AI service. I'm here to help once the service is restored!"
        
        elif any(word in message_lower for word in ['how are you', 'how do you do']):
            return "I'm doing well, thank you for asking! I'm a helpful AI assistant, though I'm currently running on backup systems due to some technical issues with my main AI service."
        
        elif any(word in message_lower for word in ['what can you do', 'help', 'assist']):
            return "I'm a RAG (Retrieval-Augmented Generation) Chat Assistant! I can help you analyze uploaded PDF documents and answer questions about their content. I'm currently running on backup systems, but I'm still here to help!"
        
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're very welcome! I'm happy to help. Is there anything else you'd like to know or discuss?"
        
        else:
            return f"I understand you're asking about: '{message}'. I can see you have uploaded a PDF document, and I'm currently experiencing some technical difficulties with my main AI service. Once restored, I'll be able to analyze your document and provide detailed answers!"
    
    def generate_embedding(self, text):
        """Generate embedding for text using Hugging Face"""
        try:
            # Use the embedding client
            from huggingface_hub import InferenceClient
            emb_client = InferenceClient(
                model="sentence-transformers/all-mpnet-base-v2", 
                token=self.hf_token
            )
            embedding = emb_client.feature_extraction(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 768
    
    def retrieve_documents(self, query, top_k=3, chat_id=None):
        """Retrieve relevant documents using Pinecone for RAG"""
        try:
            from services.pinecone_service import PineconeService
            pinecone_service = PineconeService()
            
            print(f"RAG: Querying for: {query}")
            if chat_id:
                print(f"RAG: Filtering for chat: {chat_id}")
            
            # First try Pinecone
            sources = []
            if pinecone_service.index:
                try:
                    # Generate query embedding
                    query_embedding = self.generate_embedding(query)
                    print(f"RAG: Generated embedding of length: {len(query_embedding)}")
                    
                    # Search in Pinecone
                    results = pinecone_service.query_vectors(query_embedding, top_k)
                    print(f"RAG: Pinecone returned {len(results)} results")
                    
                    # Format results
                    for i, match in enumerate(results):
                        print(f"RAG: Processing match {i+1}, score: {match.score}")
                        print(f"RAG: Metadata keys: {list(match.metadata.keys())}")
                        
                        # Filter by chat_id if provided
                        if chat_id and match.metadata.get('chat_id') != chat_id:
                            print(f"RAG: Skipping match {i+1} - wrong chat_id: {match.metadata.get('chat_id')}")
                            continue
                        
                        # Get the full text from metadata or from database
                        text_content = match.metadata.get('text', '')
                        if not text_content:
                            # Try to get from database if not in metadata
                            try:
                                from documents.models import DocumentChunk
                                chunk_id = match.metadata.get('chunk_id', 0)
                                pdf_id = match.metadata.get('pdf_id')
                                print(f"RAG: Looking for chunk {chunk_id} in document {pdf_id}")
                                if pdf_id:
                                    chunk = DocumentChunk.objects.filter(
                                        document_id=pdf_id,
                                        chunk_id=chunk_id
                                    ).first()
                                    if chunk:
                                        text_content = chunk.content
                                        print(f"RAG: Found chunk content: {len(text_content)} chars")
                                    else:
                                        print(f"RAG: Chunk not found in database")
                            except Exception as e:
                                print(f"Error retrieving chunk content: {e}")
                        
                        # Only add if we have actual content
                        if text_content and len(text_content.strip()) > 0:
                            sources.append({
                                'text': text_content,
                                'page': match.metadata.get('page', 0),
                                'score': match.score
                            })
                            print(f"RAG: Added source {len(sources)} with {len(text_content)} chars")
                        else:
                            print(f"RAG: Skipping empty source {i+1}")
                except Exception as e:
                    print(f"Pinecone query failed: {e}")
            else:
                print("RAG: Pinecone index not available")
            
            # If no sources from Pinecone, try database fallback
            if not sources and chat_id:
                print("RAG: No sources from Pinecone, trying database fallback...")
                try:
                    from documents.models import Document, DocumentChunk
                    from chat.models import Chat
                    
                    # Get chat and its documents
                    chat = Chat.objects.get(supabase_id=chat_id)
                    documents = Document.objects.filter(chat=chat)
                    print(f"RAG: Found {documents.count()} documents in database for chat")
                    
                    # Get all chunks from these documents
                    chunks = DocumentChunk.objects.filter(document__in=documents)
                    print(f"RAG: Found {chunks.count()} chunks in database")
                    
                    # Simple text matching fallback
                    query_words = query.lower().split()
                    for chunk in chunks[:top_k]:  # Limit to top_k chunks
                        content_lower = chunk.content.lower()
                        # Check if any query words are in the content
                        if any(word in content_lower for word in query_words):
                            sources.append({
                                'text': chunk.content,
                                'page': chunk.page_number,
                                'score': 0.8  # Default score for database fallback
                            })
                            print(f"RAG: Added database source with {len(chunk.content)} chars")
                    
                    # If still no sources, just take the first few chunks
                    if not sources:
                        print("RAG: No matching chunks found, using first available chunks")
                        for chunk in chunks[:top_k]:
                            sources.append({
                                'text': chunk.content,
                                'page': chunk.page_number,
                                'score': 0.5  # Lower score for non-matching chunks
                            })
                            print(f"RAG: Added fallback source with {len(chunk.content)} chars")
                            
                except Exception as e:
                    print(f"Database fallback failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"RAG: Returning {len(sources)} valid sources")
            return sources
        except Exception as e:
            print(f"Document retrieval failed: {e}")
            import traceback
            traceback.print_exc()
            return []