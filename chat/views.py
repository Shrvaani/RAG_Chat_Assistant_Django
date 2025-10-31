from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Chat, Message
from .services import ConversationService
from accounts.models import UserProfile
from documents.models import Document, DocumentChunk
import json

def ensure_user_profile(user):
    """Ensure user has a UserProfile, create if not exists"""
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(user=user)

def get_guest_user():
    """Return a shared guest user account (created on first use)."""
    from django.contrib.auth.models import User
    guest, _ = User.objects.get_or_create(username='guest_user', defaults={'password': '!', 'email': 'guest@example.com'})
    return guest

def get_or_create_guest_chat(request):
    """Create or fetch the session-bound guest chat."""
    chat_id = request.session.get('guest_chat_id')
    if chat_id:
        try:
            return Chat.objects.get(supabase_id=chat_id)
        except Chat.DoesNotExist:
            pass
    # create new
    import uuid
    chat_id = str(uuid.uuid4())
    chat = Chat.objects.create(supabase_id=chat_id, user=get_guest_user(), title='Guest Chat')
    request.session['guest_chat_id'] = chat_id
    return chat

def dashboard_view(request):
    """Main chat dashboard"""
    if request.user.is_authenticated:
        ensure_user_profile(request.user)
        chats = Chat.objects.filter(user=request.user)
    else:
        # guest view: expose single guest chat ID
        chat = get_or_create_guest_chat(request)
        chats = [chat]
    return render(request, 'chat/dashboard.html', {'chats': chats})

def landing_view(request):
    """Public landing page. Redirect authenticated users to dashboard."""
    if request.user.is_authenticated:
        return redirect('chat:dashboard')
    return render(request, 'chat/landing_public.html')

@login_required
def chat_detail_view(request, chat_id):
    """Individual chat view"""
    chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
    messages = Message.objects.filter(chat=chat).order_by('created_at')
    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chats(request):
    """Get user's chats"""
    chats = Chat.objects.filter(user=request.user)
    return Response([{
        'id': chat.supabase_id,
        'title': chat.title,
        'created_at': chat.created_at
    } for chat in chats])

@api_view(['POST'])
@permission_classes([AllowAny])
def create_chat(request):
    """Create new chat"""
    print(f"Create chat request from user: {request.user}")
    title = request.data.get('title', 'New Chat')
    print(f"Creating chat with title: {title}")
    
    try:
        if request.user.is_authenticated:
            print("Ensuring user profile...")
            user_profile = ensure_user_profile(request.user)
            print(f"User profile: {user_profile}")
            owner = request.user
        else:
            owner = get_guest_user()
        # Create a simple chat ID
        import uuid
        chat_id = str(uuid.uuid4())
        print(f"Generated chat ID: {chat_id}")
        
        # Create in Django
        print("Creating chat in database...")
        chat = Chat.objects.create(
            supabase_id=chat_id,
            user=owner,
            title=title
        )
        print(f"Chat created successfully: {chat.id}")
        
        return Response({
            'id': chat.supabase_id,
            'title': chat.title,
            'created_at': chat.created_at
        })
    except Exception as e:
        print(f"Error creating chat: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """Send message and get response"""
    chat_id = request.data.get('chat_id')
    message = request.data.get('message')
    use_rag = request.data.get('use_rag', True)
    
    if not chat_id or not message:
        return Response({'error': 'chat_id and message are required'}, status=400)
    
    try:
        if request.user.is_authenticated:
            chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
        else:
            # Guest: prefer session-bound chat, but if a valid guest chat_id was
            # created previously (e.g., in another tab) bind the session to it.
            guest_chat = get_or_create_guest_chat(request)
            if guest_chat.supabase_id != chat_id:
                try:
                    candidate = Chat.objects.get(supabase_id=chat_id, user=get_guest_user())
                    # Rebind session to this guest chat
                    request.session['guest_chat_id'] = candidate.supabase_id
                    chat = candidate
                except Chat.DoesNotExist:
                    return Response({'error': 'Invalid chat for guest'}, status=403)
            else:
                chat = guest_chat
        
        # Save user message to database
        Message.objects.create(
            chat=chat,
            role='user',
            content=message,
            sources=[]
        )
        
        # Generate AI response with conversation context
        conversation_service = ConversationService()
        response, sources = conversation_service.generate_response_with_context(
            message, chat_id, use_rag
        )
        
        # Save assistant response to database
        Message.objects.create(
            chat=chat,
            role='assistant',
            content=response,
            sources=sources
        )
        
        return Response({
            'response': response,
            'sources': sources
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_messages(request, chat_id):
    """Get messages for a chat"""
    try:
        if request.user.is_authenticated:
            chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
        else:
            chat = get_or_create_guest_chat(request)
            if chat.supabase_id != chat_id:
                try:
                    candidate = Chat.objects.get(supabase_id=chat_id, user=get_guest_user())
                    request.session['guest_chat_id'] = candidate.supabase_id
                    chat = candidate
                except Chat.DoesNotExist:
                    return Response({'error': 'Invalid chat for guest'}, status=403)
        messages = Message.objects.filter(chat=chat).order_by('created_at')
        return Response([{
            'role': message.role,
            'content': message.content,
            'sources': message.sources or [],
            'created_at': message.created_at
        } for message in messages])
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat(request, chat_id):
    """Delete a chat and all its associated data"""
    try:
        print(f"Delete request for chat: {chat_id}, user: {request.user}")
        chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
        print(f"Found chat: {chat.title}")
        
        # Delete associated documents and chunks
        documents = Document.objects.filter(chat=chat)
        print(f"Found {documents.count()} documents to delete")
        
        for document in documents:
            # Delete document chunks
            chunks = DocumentChunk.objects.filter(document=document)
            print(f"Deleting {chunks.count()} chunks for document {document.id}")
            chunks.delete()
            
            # Delete document file if it exists
            if document.file_path and document.file_path.name:
                try:
                    document.file_path.delete(save=False)
                    print(f"Deleted file: {document.file_path.name}")
                except Exception as e:
                    print(f"Error deleting file: {e}")
        
        # Delete documents
        documents.delete()
        print("Deleted all documents")
        
        # Delete messages
        messages = Message.objects.filter(chat=chat)
        print(f"Deleting {messages.count()} messages")
        messages.delete()
        
        # Delete chat
        chat_title = chat.title
        chat.delete()
        print(f"Deleted chat: {chat_title}")
        
        return Response({'success': True, 'message': 'Chat deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting chat: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def rename_chat(request, chat_id):
    """Rename a chat"""
    try:
        chat = get_object_or_404(Chat, supabase_id=chat_id, user=request.user)
        new_title = request.data.get('title', '').strip()
        
        if not new_title:
            return Response({'error': 'Title cannot be empty'}, status=400)
        
        chat.title = new_title
        chat.save()
        
        return Response({
            'success': True, 
            'message': 'Chat renamed successfully',
            'new_title': new_title
        })
        
    except Exception as e:
        print(f"Error renaming chat: {e}")
        return Response({'error': str(e)}, status=500)

