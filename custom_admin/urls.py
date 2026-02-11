from django.urls import path

from custom_admin import views

app_name = "custom_admin"

urlpatterns = [
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("", views.dashboard, name="dashboard"),

    path("chefs/", views.chef_list, name="chef_list"),
    path("chefs/add/", views.chef_add, name="chef_add"),
    path("chefs/edit/<int:pk>/", views.chef_edit, name="chef_edit"),
    path("chefs/delete/<int:pk>/", views.chef_delete, name="chef_delete"),

    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/view/<int:pk>/", views.booking_view, name="booking_view"),
    path("bookings/update-status/<int:pk>/", views.booking_update_status, name="booking_update_status"),
    path("bookings/cancel/<int:pk>/", views.booking_cancel, name="booking_cancel"),
    path("bookings/delete/<int:pk>/", views.booking_delete, name="booking_delete"),
    path("bookings/hard-delete/<int:pk>/", views.booking_hard_delete, name="booking_hard_delete"),

    path("blogs/", views.blog_list, name="blog_list"),
    path("blogs/add/", views.blog_add, name="blog_add"),
    path("blogs/edit/<int:pk>/", views.blog_edit, name="blog_edit"),
    path("blogs/toggle-publish/<int:pk>/", views.blog_toggle_publish, name="blog_toggle_publish"),
    path("blogs/delete/<int:pk>/", views.blog_delete, name="blog_delete"),

    path("users/", views.user_list, name="user_list"),
    path("users/view/<int:pk>/", views.user_view, name="user_view"),
    path("users/edit/<int:pk>/", views.user_edit, name="user_edit"),
    path("users/toggle-active/<int:pk>/", views.user_toggle_active, name="user_toggle_active"),
    path("users/delete/<int:pk>/", views.user_delete, name="user_delete"),

    path("contact-queries/", views.contact_query_list, name="contact_query_list"),
    path("contact-queries/view/<int:pk>/", views.contact_query_view, name="contact_query_view"),
    path("contact-queries/delete/<int:pk>/", views.contact_query_delete, name="contact_query_delete"),
]
