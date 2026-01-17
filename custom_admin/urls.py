from django.urls import path
from custom_admin import views

app_name = "custom_admin"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Chef CRUD
    path("chefs/", views.chef_list, name="chef_list"),
    path("chefs/add/", views.chef_add, name="chef_add"),
    path("chefs/edit/<int:pk>/", views.chef_edit, name="chef_edit"),
    path("chefs/delete/<int:pk>/", views.chef_delete, name="chef_delete"),

    # Bookings
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/view/<int:pk>/", views.booking_view, name="booking_view"),
    path("bookings/delete/<int:pk>/", views.booking_delete, name="booking_delete"),

    # Users / Profiles
    path("users/", views.user_list, name="user_list"),
    path("users/view/<int:pk>/", views.user_view, name="user_view"),
    path("users/edit/<int:pk>/", views.user_edit, name="user_edit"),
    path("users/delete/<int:pk>/", views.user_delete, name="user_delete"),
]
