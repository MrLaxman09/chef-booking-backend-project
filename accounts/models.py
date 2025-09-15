from django.db import models
from django.conf import settings

def user_directory_path(instance, filename):
    return f'profile_images/user_{instance.user.id}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    education = models.CharField(max_length=255, blank=True)
    experience = models.IntegerField(default=0)
    speciality = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    dishes = models.CharField(max_length=255, default="Not specified")

    profile_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    # ❌ Remove this line: work_images = models.ImageField(...) → It's now handled in WorkImage model

    def __str__(self):
        return self.user.username

def work_image_upload_path(instance, filename):
    return f'work_images/{instance.profile.user.username}/{filename}'


class WorkImage(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='work_images')
    image = models.ImageField(upload_to=work_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username} - Image"
