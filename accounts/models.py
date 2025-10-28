from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """Extended user profile with Supabase integration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    supabase_user_id = models.CharField(max_length=36, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

