from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'supabase_user_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')

