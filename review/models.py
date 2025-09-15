from django.db import models
from django.contrib.auth.models import User
from booking.models import Booking

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def chef(self):
        return self.booking.chef

class ChefResponse(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    response = models.TextField()
    responded_at = models.DateTimeField(auto_now_add=True)