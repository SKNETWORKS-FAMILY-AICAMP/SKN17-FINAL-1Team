from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'nickname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'nickname')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인정보', {'fields': ('nickname', 'profile_image')}),
        ('권한', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(User, CustomUserAdmin)
