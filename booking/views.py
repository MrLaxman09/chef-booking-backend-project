from datetime import date as dt_date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile
from .forms import ChefForm
from .models import BlogPost, Booking, Chef


def home(request):
    return render(request, "booking/home.html")


def about(request):
    return render(request, "booking/about.html")


def blog_list(request):
    posts = BlogPost.objects.select_related("author").filter(is_published=True).order_by("-created_at")
    return render(request, "booking/blog_list.html", {"posts": posts})


def blog_detail(request, pk):
    post = get_object_or_404(
        BlogPost.objects.select_related("author").filter(is_published=True),
        pk=pk,
    )
    return render(request, "booking/blog_detail.html", {"post": post})


@login_required
def chef_list(request):
    query = request.GET.get("q", "").strip()
    chefs = Chef.objects.select_related("user", "user__profile").all()
    if query:
        chefs = chefs.filter(
            Q(name__icontains=query)
            | Q(specialty__icontains=query)
            | Q(experience__icontains=query)
        )

    return render(
        request,
        "booking/chef_list.html",
        {
            "chefs": chefs,
            "query": query,
        },
    )


@login_required
def dashboard(request):
    now = timezone.now()
    current_date = now.date()
    current_time = now.time().replace(microsecond=0)
    past_bookings_q = Q(date__lt=current_date) | Q(date=current_date, time__lt=current_time)

    customer_bookings = (
        Booking.objects.select_related("chef", "chef__user")
        .filter(customer=request.user)
        .exclude(past_bookings_q)
        .order_by("-date", "-time")
    )
    customer_past_bookings = (
        Booking.objects.select_related("chef", "chef__user")
        .filter(customer=request.user)
        .filter(past_bookings_q)
        .order_by("-date", "-time")
    )
    chef_bookings = (
        Booking.objects.select_related("customer", "chef")
        .filter(chef__user=request.user)
        .exclude(past_bookings_q)
        .order_by("-date", "-time")
    )
    chef_past_bookings = (
        Booking.objects.select_related("customer", "chef")
        .filter(chef__user=request.user)
        .filter(past_bookings_q)
        .order_by("-date", "-time")
    )
    pending_count = chef_bookings.filter(status="Pending").count()

    return render(
        request,
        "booking/dashboard.html",
        {
            "bookings": chef_bookings,
            "past_bookings": chef_past_bookings,
            "cos_bookings": customer_bookings,
            "past_cos_bookings": customer_past_bookings,
            "pending_count": pending_count,
        },
    )


@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking.objects.select_related("chef__user"), id=booking_id)

    if request.user != booking.chef.user:
        messages.error(request, "You are not allowed to update this booking.")
        return redirect("dashboard")

    if status not in {"Accepted", "Rejected"}:
        messages.error(request, "Invalid booking status.")
        return redirect("dashboard")

    booking.status = status
    booking.save(update_fields=["status"])
    messages.success(request, f"Booking marked as {status.lower()}.")
    return redirect("dashboard")


@login_required
@require_POST
def remove_booking(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("customer"),
        id=booking_id,
        customer=request.user,
    )
    if not booking.is_past:
        return HttpResponseBadRequest("Only past bookings can be removed from the list.")

    booking.soft_delete(by_user=request.user)
    messages.success(request, "Booking removed from your list.")
    return redirect("dashboard")


@login_required
@require_POST
def clear_past_bookings(request):
    now = timezone.now()
    current_date = now.date()
    current_time = now.time().replace(microsecond=0)
    past_bookings_q = Q(date__lt=current_date) | Q(date=current_date, time__lt=current_time)

    updated = (
        Booking.objects.filter(customer=request.user)
        .filter(past_bookings_q)
        .update(is_deleted=True, deleted_at=now, deleted_by_id=request.user.id)
    )
    if updated:
        messages.success(request, f"{updated} past booking(s) removed from your list.")
    else:
        messages.info(request, "No past bookings were available to remove.")
    return redirect("dashboard")


@login_required
def book_chef(request, chef_id):
    chef = get_object_or_404(Chef, id=chef_id)
    if request.user == chef.user:
        messages.error(request, "You cannot book your own chef profile.")
        return redirect("chef_list")

    if request.method == "POST":
        booking_date = request.POST.get("date")
        booking_time = request.POST.get("time")
        persons = int(request.POST.get("person", "0"))

        if persons < 1:
            messages.error(request, "Please select at least one guest.")
            return redirect("book_chef", chef_id=chef.id)

        if booking_date and booking_date < dt_date.today().isoformat():
            messages.error(request, "Booking date cannot be in the past.")
            return redirect("book_chef", chef_id=chef.id)

        total_price = chef.price_per_person * persons

        Booking.objects.create(
            customer=request.user,
            chef=chef,
            date=booking_date,
            time=booking_time,
            person=persons,
            total_price=total_price,
            status="Pending",
        )
        messages.success(request, "Booking request submitted successfully.")
        return redirect("dashboard")
    return render(request, "booking/book_chef.html", {"chef": chef})


@login_required
def become_chef(request):
    if Chef.objects.filter(user=request.user).exists():
        messages.info(request, "You already have a chef profile.")
        return redirect("chef_list")

    if request.method == "POST":
        form = ChefForm(request.POST, request.FILES)
        if form.is_valid():
            chef = form.save(commit=False)
            chef.user = request.user
            chef.save()
            messages.success(request, "Chef profile created successfully.")
            return redirect("chef_list")
    else:
        profile = Profile.objects.filter(user=request.user).first()
        form = ChefForm(
            initial={
                "name": (profile.name if profile and profile.name else request.user.username),
                "experience": profile.experience if profile else 0,
            }
        )

    return render(request, "booking/become_chef.html", {"form": form})


@login_required
def user_profile(request):
    return redirect("profile_detail", username=request.user.username)
