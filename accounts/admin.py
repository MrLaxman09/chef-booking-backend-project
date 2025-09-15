# admin.py
from django.contrib import admin
from .models import Profile, WorkImage

admin.site.register(Profile)
admin.site.register(WorkImage)
