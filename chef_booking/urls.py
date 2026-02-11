from django.contrib import admin
from django.urls import path, include
from booking import views as booking_views
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("myadmin/", include("custom_admin.urls", namespace="custom_admin")),


    # Home and Chef Pages
    path('', booking_views.home, name='home'),
    path('about/', booking_views.about, name='about'),
    path('contact/submit/', booking_views.submit_contact_query, name='submit_contact_query'),
    path('blog/', booking_views.blog_list, name='blog_list'),
    path('<int:pk>/', booking_views.blog_detail, name='blog_detail'),
    
    
    path('chefs/', booking_views.chef_list, name='chef_list'),
    path('dashboard/', booking_views.dashboard, name='dashboard'),
    path('book/<int:chef_id>/', booking_views.book_chef, name='book_chef'),
    path('bookings/remove/<int:booking_id>/', booking_views.remove_booking, name='remove_booking'),
    path('bookings/clear-past/', booking_views.clear_past_bookings, name='clear_past_bookings'),

    # Booking and Chef Actions
    path('become-chef/', booking_views.become_chef, name='become_chef'),
    # path('my-bookings/', booking_views.my_bookings, name='my_bookings'),
    # path('view-bookings/', booking_views.view_bookings, name='view_bookings'),
    path('update-booking/<int:booking_id>/<str:status>/', booking_views.update_booking_status, name='update_booking_status'),


    # User Auth
    path('accounts/login/', accounts_views.RoleAwareLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),  # Login, logout, password reset
    path('signup/', accounts_views.signup, name='signup'),
    path('user_profile/', booking_views.user_profile, name='user_profile'),
    path('profile/edit/', accounts_views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', accounts_views.profile_detail, name='profile_detail'),
    # path('profile/<str:username>/', accounts_views.profile_detail, name='profile_detail'),
    path('profile/<str:username>/<int:booking_id>/<int:review_id>/', accounts_views.profile_detail, name='profile_detail_with_review'),

    path('profile/<str:username>/upload-images/', accounts_views.upload_work_images, name='upload_work_images'),
    path('profile/<str:username>/work-images/<int:image_id>/update/', accounts_views.update_work_image, name='update_work_image'),
    path('profile/<str:username>/work-images/<int:image_id>/delete/', accounts_views.delete_work_image, name='delete_work_image'),

    

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



