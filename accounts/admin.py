from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = UserAdmin.list_display + ('username', 'email', 'convoyName', 'phoneNumber', 'profilePicture')
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('convoyName', 'phoneNumber', 'profilePicture'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'convoyName', 'phoneNumber', 'profilePicture'),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name', 'convoyName', 'phoneNumber')
    ordering = ('email',)
