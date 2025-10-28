from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Document, DocumentChunk
from chat.models import Chat
from services.supabase_service import SupabaseService
from services.pinecone_service import PineconeService
from services.ai_service import AIService
from langchain_community.document_loaders import PyMuPDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import os
import tempfile
import uuid

@login_required
def upload_document(request, chat_id):
    """Upload and process PDF document"""
    try:
        chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
        print(f"Upload request for chat: {chat_id}, user: {request.user}")
        
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')
            print(f"Uploaded file: {uploaded_file}")
            
            if not uploaded_file:
                return JsonResponse({'success': False, 'error': 'No file provided'})
            
            if not uploaded_file.name.lower().endswith('.pdf'):
                return JsonResponse({'success': False, 'error': 'Please upload a PDF file'})
            
            try:
                print(f"Creating document record for: {uploaded_file.name}")
                # Create document record
                document = Document.objects.create(
                    chat=chat,
                    filename=uploaded_file.name,
                    file_path=uploaded_file
                )
                print(f"Created document: {document.id} for chat: {chat_id}")
                
                # Process PDF
                print("Starting PDF processing...")
                success = process_pdf_document(document, uploaded_file, chat_id)
                print(f"PDF processing result: {success}")
                
                if success:
                    return JsonResponse({
                        'success': True, 
                        'message': f'PDF "{uploaded_file.name}" uploaded and processed successfully!'
                    })
                else:
                    return JsonResponse({
                        'success': False, 
                        'error': 'PDF uploaded but processing failed. Check server logs for details.'
                    })
                    
            except Exception as e:
                print(f"Upload error: {e}")
                import traceback
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': f'Upload failed: {str(e)}'})
        
        return render(request, 'documents/upload.html', {'chat': chat})
        
    except Exception as e:
        print(f"Upload view error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

def process_pdf_document(document, uploaded_file, chat_id):
    """Process PDF: extract text, chunk, embed, and store in Pinecone"""
    temp_path = None
    try:
        print(f"Starting PDF processing for document: {document.id}")
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            temp_path = tmp.name
        
        print(f"Saved PDF to temp file: {temp_path}")
        
        # Load PDF with better error handling
        pages = []
        try:
            print("Trying PyMuPDFLoader...")
            loader = PyMuPDFLoader(temp_path)
            pages = loader.load()
            print(f"PyMuPDFLoader loaded {len(pages)} pages")
        except Exception as e:
            print(f"PyMuPDFLoader failed: {e}")
            try:
                print("Trying PyPDFLoader...")
                loader = PyPDFLoader(temp_path)
                pages = loader.load()
                print(f"PyPDFLoader loaded {len(pages)} pages")
            except Exception as e2:
                print(f"PyPDFLoader also failed: {e2}")
                raise Exception(f"Both PDF loaders failed: {e}, {e2}")
        
        if not pages:
            print("No pages loaded from PDF")
            return False
        
        print(f"Processing {len(pages)} pages")
        
        # Split into chunks
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500, 
                chunk_overlap=400
            )
            chunks = splitter.split_documents(pages)
            print(f"Split into {len(chunks)} chunks")
        except Exception as e:
            print(f"Text splitting failed: {e}")
            return False
        
        # Generate embeddings with fallback
        ai_service = AIService()
        texts = [chunk.page_content for chunk in chunks]
        embeddings = []
        
        print("Generating embeddings...")
        for i, text in enumerate(texts):
            try:
                embedding = ai_service.generate_embedding(text)
                embeddings.append(embedding)
                if i % 5 == 0:  # Progress indicator
                    print(f"Generated {i+1}/{len(texts)} embeddings")
            except Exception as e:
                print(f"Embedding generation failed for chunk {i}: {e}")
                # Use zero vector as fallback
                embeddings.append([0.0] * 768)
        
        print(f"Generated {len(embeddings)} embeddings")
        
        # Store in Pinecone (optional)
        try:
            pinecone_service = PineconeService()
            if pinecone_service.index:
                print("Clearing old vectors for this chat...")
                pinecone_service.clear_old_vectors(chat_id)
                
                print("Storing vectors in Pinecone...")
                vectors_to_upsert = []
                for i, (embedding, text, chunk) in enumerate(zip(embeddings, texts, chunks)):
                    vector_id = f"{document.id}_{i}"
                    metadata = {
                        'pdf_id': str(document.id),
                        'chunk_id': i,
                        'page': chunk.metadata.get('page', 0),
                        'text': text[:1000],  # Limit metadata size
                        'chat_id': chat_id
                    }
                    vectors_to_upsert.append((vector_id, embedding, metadata))
                
                pinecone_service.upsert_vectors(vectors_to_upsert)
                print(f"Stored {len(vectors_to_upsert)} vectors in Pinecone")
            else:
                print("Pinecone not available, skipping vector storage")
        except Exception as e:
            print(f"Pinecone storage failed: {e}")
            # Continue without Pinecone
        
        # Store chunks in database
        print("Storing chunks in database...")
        for i, (text, chunk) in enumerate(zip(texts, chunks)):
            try:
                DocumentChunk.objects.create(
                    document=document,
                    chunk_id=i,
                    page_number=chunk.metadata.get('page', 0),
                    content=text,
                    embedding=embeddings[i] if i < len(embeddings) else []
                )
            except Exception as e:
                print(f"Failed to store chunk {i}: {e}")
                # Continue with other chunks
        
        print(f"Successfully processed PDF with {len(chunks)} chunks")
        return True
        
    except Exception as e:
        print(f"PDF processing error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                print(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                print(f"Failed to clean up temp file: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_documents(request, chat_id):
    """Get documents for a chat"""
    try:
        print(f"Getting documents for chat: {chat_id}, user: {request.user}")
        chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
        documents = Document.objects.filter(chat=chat)
        print(f"Found {documents.count()} documents")
        
        result = [{
            'id': str(doc.id),
            'filename': doc.filename,
            'created_at': doc.uploaded_at
        } for doc in documents]
        
        print(f"Returning documents: {result}")
        return Response(result)
    except Exception as e:
        print(f"Error getting documents: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_document(request, document_id):
    """Get document chunks for viewing"""
    try:
        document = get_object_or_404(Document, id=document_id, chat__user=request.user)
        chunks = DocumentChunk.objects.filter(document=document).order_by('page_number', 'chunk_id')
        
        return Response({
            'success': True,
            'document': {
                'id': str(document.id),
                'filename': document.filename,
                'created_at': document.created_at
            },
            'chunks': [{
                'chunk_id': chunk.chunk_id,
                'page_number': chunk.page_number,
                'content': chunk.content
            } for chunk in chunks]
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, document_id):
    """Delete a document and all its associated data"""
    try:
        print(f"Delete document request for: {document_id}, user: {request.user}")
        document = get_object_or_404(Document, id=document_id, chat__user=request.user)
        print(f"Found document: {document.filename}")
        
        # Delete document chunks
        chunks = DocumentChunk.objects.filter(document=document)
        print(f"Deleting {chunks.count()} chunks for document {document.id}")
        chunks.delete()
        
        # Delete from Pinecone if available
        try:
            from services.pinecone_service import PineconeService
            pinecone_service = PineconeService()
            if pinecone_service.index:
                # Delete vectors with document ID
                pinecone_service.delete_vectors([f"{document.id}_{i}" for i in range(100)])  # Delete up to 100 chunks
                print(f"Deleted vectors from Pinecone for document {document.id}")
        except Exception as e:
            print(f"Error deleting from Pinecone: {e}")
        
        # Delete document file if it exists
        if document.file_path and document.file_path.name:
            try:
                document.file_path.delete(save=False)
                print(f"Deleted file: {document.file_path.name}")
            except Exception as e:
                print(f"Error deleting file: {e}")
        
        # Delete document record
        document_filename = document.filename
        document.delete()
        print(f"Deleted document: {document_filename}")
        
        return Response({
            'success': True, 
            'message': f'Document "{document_filename}" deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting document: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

