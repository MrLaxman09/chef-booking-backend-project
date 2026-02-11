from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


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


class BookingQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def archived(self):
        return self.filter(is_deleted=True)


class ActiveBookingManager(models.Manager):
    def get_queryset(self):
        return BookingQuerySet(self.model, using=self._db).active()


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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_bookings",
    )

    objects = ActiveBookingManager()
    all_objects = BookingQuerySet.as_manager()

    def __str__(self):
        return f"{self.customer.username} booked {self.chef.name}"

    @property
    def scheduled_at(self):
        return datetime.combine(self.date, self.time).replace(tzinfo=dt_timezone.utc)

    @property
    def is_past(self):
        return self.scheduled_at < timezone.now()

    def soft_delete(self, by_user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    class Meta:
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["status", "date"]),
            models.Index(fields=["is_deleted", "date"]),
        ]


from django.contrib.auth.models import User

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="blog_images/")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return self.title
