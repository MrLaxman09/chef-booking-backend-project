from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from booking.models import Booking

from .forms import ProfileForm, SignUpForm, WorkImageForm
from .models import Profile, WorkImage


class RoleAwareLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        if self.request.user.is_superuser:
            return reverse("custom_admin:dashboard")
        return reverse("chef_list")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Account created successfully.")
            return redirect("chef_list")
        messages.error(request, "Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def my_bookings(request):
    bookings = (
        Booking.objects.select_related("chef")
        .filter(customer=request.user)
        .order_by("-date", "-time")
    )
    return render(request, "booking/my_bookings.html", {"bookings": bookings})


def profile_detail(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(
        Profile.objects.select_related("user").prefetch_related("work_images"),
        user=profile_user,
    )
    is_owner = request.user == profile_user
    is_chef = hasattr(profile_user, "chef")

    return render(
        request,
        "accounts/profile_detail.html",
        {
            "profile": profile,
            "profile_user": profile_user,
            "is_owner": is_owner,
            "is_chef": is_chef,
        },
    )


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile_detail", username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {"form": form})


@login_required
def upload_work_images(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    if request.user != profile.user:
        messages.error(request, "You can only manage images for your own profile.")
        return redirect("profile_detail", username=username)

    if request.method == "POST":
        form = WorkImageForm(request.POST, request.FILES)
        if form.is_valid():
            work = form.save(commit=False)
            work.profile = profile
            work.save()
            messages.success(request, "Image uploaded successfully.")
            return redirect("upload_work_images", username=username)
        messages.error(request, "Please select a valid image file.")
    else:
        form = WorkImageForm()

    images = profile.work_images.all().order_by("-uploaded_at")

    return render(
        request,
        "accounts/upload_work_images.html",
        {"form": form, "profile": profile, "images": images},
    )


@login_required
@require_POST
def update_work_image(request, username, image_id):
    profile = get_object_or_404(Profile, user__username=username)
    if request.user != profile.user:
        messages.error(request, "You can only update your own gallery images.")
        return redirect("profile_detail", username=username)

    work_image = get_object_or_404(WorkImage, id=image_id, profile=profile)
    form = WorkImageForm(request.POST, request.FILES, instance=work_image)
    if form.is_valid():
        form.save()
        messages.success(request, "Image updated successfully.")
    else:
        messages.error(request, "Please select a valid replacement image.")
    return redirect("upload_work_images", username=username)


@login_required
@require_POST
def delete_work_image(request, username, image_id):
    profile = get_object_or_404(Profile, user__username=username)
    if request.user != profile.user:
        messages.error(request, "You can only delete your own gallery images.")
        return redirect("profile_detail", username=username)

    work_image = get_object_or_404(WorkImage, id=image_id, profile=profile)
    work_image.delete()
    messages.success(request, "Image deleted from gallery.")
    return redirect("upload_work_images", username=username)
