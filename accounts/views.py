from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.forms import modelformset_factory
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from booking.models import Booking

from .forms import ProfileForm, SignUpForm
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

    work_image_formset = modelformset_factory(WorkImage, fields=("image",), extra=2, can_delete=True)

    if request.method == "POST":
        formset = work_image_formset(
            request.POST,
            request.FILES,
            queryset=WorkImage.objects.filter(profile=profile),
        )
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.profile = profile
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Work images updated.")
            return redirect("profile_detail", username=username)
    else:
        formset = work_image_formset(queryset=WorkImage.objects.filter(profile=profile))

    return render(
        request,
        "accounts/upload_work_images.html",
        {"formset": formset, "profile": profile},
    )
