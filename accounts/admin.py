from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, Post, Image

class MyUserAdmin(UserAdmin):
    model = MyUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

class ImageInline(admin.TabularInline):
    model = Image

class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at', 'updated_at')
    search_fields = ('user__email', 'text')
    list_filter = ('created_at', 'updated_at')
    inlines = [ImageInline]

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Post, PostAdmin)
