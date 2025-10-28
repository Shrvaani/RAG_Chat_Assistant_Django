from django.conf import settings
import json
import requests

class SupabaseService:
    """Service for Supabase integration using REST API"""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.headers = {
            'apikey': self.key,
            'Authorization': f'Bearer {self.key}',
            'Content-Type': 'application/json'
        }
        
        # Check if Supabase is configured
        if not self.url or not self.key:
            print("Warning: Supabase URL or KEY not configured. Supabase features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            print(f"Supabase service initialized with URL: {self.url}")
    
    def create_user(self, user_id, username, email):
        """Create user in Supabase"""
        if not self.enabled:
            print("Supabase is not enabled, skipping user creation")
            return None
            
        try:
            print(f"Attempting to create Supabase user: {user_id}, {username}, {email}")
            data = {
                "id": user_id,
                "username": username,
                "email": email
            }
            print(f"Supabase URL: {self.url}")
            print(f"Request data: {data}")
            
            response = requests.post(
                f"{self.url}/rest/v1/users",
                headers=self.headers,
                json=data
            )
            print(f"Supabase response status: {response.status_code}")
            print(f"Supabase response text: {response.text}")
            
            if response.status_code == 201:
                try:
                    if response.text.strip():
                        user_data = response.json()
                        if isinstance(user_data, list) and len(user_data) > 0:
                            user_data = user_data[0]
                        print(f"Successfully created Supabase user: {user_data}")
                        return user_data
                    else:
                        print("Supabase returned empty response, but status was 201")
                        # Return a mock user object for successful creation
                        return {
                            'id': user_id,
                            'username': username,
                            'email': email
                        }
                except Exception as json_error:
                    print(f"JSON parsing error: {json_error}")
                    print(f"Response text: '{response.text}'")
                    # Return a mock user object for successful creation
                    return {
                        'id': user_id,
                        'username': username,
                        'email': email
                    }
            else:
                print(f"Failed to create Supabase user: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating user in Supabase: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_chats(self, user_id):
        """Get user's chats from Supabase"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/chats?user_id=eq.{user_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting user chats: {e}")
            return []
    
    def create_chat(self, user_id, title):
        """Create chat in Supabase"""
        try:
            data = {
                "user_id": user_id,
                "title": title
            }
            response = requests.post(
                f"{self.url}/rest/v1/chats",
                headers=self.headers,
                json=data
            )
            if response.status_code == 201:
                return response.json()[0]
            else:
                print(f"Supabase error: {response.status_code} - {response.text}")
                # Return a mock chat object if Supabase fails
                return {
                    'id': f"chat_{user_id}_{title.replace(' ', '_')}",
                    'user_id': user_id,
                    'title': title
                }
        except Exception as e:
            print(f"Error creating chat: {e}")
            # Return a mock chat object if Supabase fails
            return {
                'id': f"chat_{user_id}_{title.replace(' ', '_')}",
                'user_id': user_id,
                'title': title
            }
    
    def get_chat_messages(self, chat_id):
        """Get chat messages from Supabase"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/messages?chat_id=eq.{chat_id}&order=created_at",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting chat messages: {e}")
            return []
    
    def save_message(self, chat_id, role, content, sources):
        """Save message to Supabase"""
        try:
            data = {
                "chat_id": chat_id,
                "role": role,
                "content": content,
                "sources": json.dumps(sources)
            }
            response = requests.post(
                f"{self.url}/rest/v1/messages",
                headers=self.headers,
                json=data
            )
            if response.status_code == 201:
                return response.json()[0]
            return None
        except Exception as e:
            print(f"Error saving message: {e}")
            return None
    
    def upload_document(self, chat_id, filename):
        """Upload document metadata to Supabase"""
        try:
            data = {
                "chat_id": chat_id,
                "filename": filename
            }
            response = requests.post(
                f"{self.url}/rest/v1/pdfs",
                headers=self.headers,
                json=data
            )
            if response.status_code == 201:
                return response.json()[0]
            return None
        except Exception as e:
            print(f"Error uploading document: {e}")
            return None
    
    def get_chat_documents(self, chat_id):
        """Get documents for a chat"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/pdfs?chat_id=eq.{chat_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting chat documents: {e}")
            return []