from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Chef(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=200)
    experience = models.PositiveIntegerField()  # years
    team_members = models.PositiveIntegerField(
        validators=[MinValueValidator(2)],
        blank=True,
        null=True
    )
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='chef_dishes/', blank=True, null=True)


    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chef = models.ForeignKey('Chef', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    person = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.customer.username} booked {self.chef.name}"


from django.db import models
from django.contrib.auth.models import User

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="blog_images/")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
