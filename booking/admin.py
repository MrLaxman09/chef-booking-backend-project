from django.contrib import admin
from .models import Chef, Booking

admin.site.register(Chef)
admin.site.register(Booking)

from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    search_fields = ('title', 'content')
