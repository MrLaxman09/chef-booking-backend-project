from functools import wraps
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile
from booking.models import BlogPost, Booking, Chef, ContactQuery

from .forms import BlogPostForm, BookingStatusForm, ChefForm

User = get_user_model()


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse("custom_admin:login")
            return redirect(f"{login_url}?next={request.path}")
        if not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to access this module.")
        return view_func(request, *args, **kwargs)

    return wrapper


def _safe_sort(value, allowed, default):
    return value if value in allowed else default


def _past_booking_q():
    now = timezone.now()
    current_date = now.date()
    current_time = now.time().replace(microsecond=0)
    return Q(date__lt=current_date) | Q(date=current_date, time__lt=current_time)


def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("custom_admin:dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    next_url = request.GET.get("next") or request.POST.get("next") or reverse("custom_admin:dashboard")

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_superuser:
            messages.error(request, "Only superusers can access the admin dashboard.")
        else:
            login(request, user)
            return redirect(next_url)

    return render(request, "custom_admin/login.html", {"form": form, "next": next_url})


@require_POST
def admin_logout(request):
    logout(request)
    return redirect("custom_admin:login")


@admin_required
def dashboard(request):
    recent_bookings = Booking.objects.select_related("customer", "chef").order_by("-date", "-time")[:8]
    context = {
        "chefs_count": Chef.objects.count(),
        "bookings_count": Booking.objects.count(),
        "users_count": Profile.objects.count(),
        "blog_count": BlogPost.objects.count(),
        "published_blog_count": BlogPost.objects.filter(is_published=True).count(),
        "contact_queries_count": ContactQuery.objects.filter(is_deleted=False).count(),
        "recent_bookings": recent_bookings,
    }
    return render(request, "custom_admin/dashboard.html", context)


@admin_required
def chef_list(request):
    q = request.GET.get("q", "").strip()
    sort = _safe_sort(request.GET.get("sort", "newest"), {"newest", "oldest", "name", "price"}, "newest")
    order_map = {
        "newest": "-id",
        "oldest": "id",
        "name": "name",
        "price": "-price_per_person",
    }

    chefs_qs = Chef.objects.select_related("user")
    if q:
        chefs_qs = chefs_qs.filter(
            Q(name__icontains=q)
            | Q(specialty__icontains=q)
            | Q(user__username__icontains=q)
        )

    paginator = Paginator(chefs_qs.order_by(order_map[sort]), 12)
    chefs = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "custom_admin/chef_list.html",
        {"chefs": chefs, "q": q, "sort": sort},
    )


@admin_required
def chef_add(request):
    if request.method == "POST":
        form = ChefForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Chef created successfully.")
            return redirect("custom_admin:chef_list")
    else:
        form = ChefForm()
    return render(request, "custom_admin/chef_form.html", {"form": form, "action": "Add"})


@admin_required
def chef_edit(request, pk):
    chef = get_object_or_404(Chef, pk=pk)
    if request.method == "POST":
        form = ChefForm(request.POST, request.FILES, instance=chef)
        if form.is_valid():
            form.save()
            messages.success(request, "Chef updated successfully.")
            return redirect("custom_admin:chef_list")
    else:
        form = ChefForm(instance=chef)
    return render(request, "custom_admin/chef_form.html", {"form": form, "action": "Edit", "chef": chef})


@admin_required
@require_POST
def chef_delete(request, pk):
    chef = get_object_or_404(Chef, pk=pk)
    chef.delete()
    messages.success(request, "Chef deleted.")
    return redirect("custom_admin:chef_list")


@admin_required
def booking_list(request):
    q = request.GET.get("q", "").strip()
    scope = _safe_sort(request.GET.get("scope", "upcoming"), {"upcoming", "past", "archived", "all"}, "upcoming")
    sort = _safe_sort(request.GET.get("sort", "newest"), {"newest", "oldest", "status"}, "newest")
    order_map = {
        "newest": "-date",
        "oldest": "date",
        "status": "status",
    }

    bookings_qs = Booking.all_objects.select_related("customer", "chef")
    past_q = _past_booking_q()
    if scope == "upcoming":
        bookings_qs = bookings_qs.filter(is_deleted=False).exclude(past_q)
    elif scope == "past":
        bookings_qs = bookings_qs.filter(is_deleted=False).filter(past_q)
    elif scope == "archived":
        bookings_qs = bookings_qs.filter(is_deleted=True)
    else:
        bookings_qs = bookings_qs.filter(is_deleted=False)

    if q:
        bookings_qs = bookings_qs.filter(
            Q(customer__username__icontains=q)
            | Q(chef__name__icontains=q)
            | Q(status__icontains=q)
        )

    paginator = Paginator(bookings_qs.order_by(order_map[sort], "-time"), 15)
    bookings = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "custom_admin/booking_list.html",
        {
            "bookings": bookings,
            "q": q,
            "sort": sort,
            "scope": scope,
            "status_choices": Booking.STATUS_CHOICES,
        },
    )


@admin_required
def booking_view(request, pk):
    booking = get_object_or_404(Booking.all_objects.select_related("customer", "chef"), pk=pk)
    status_form = BookingStatusForm(instance=booking)
    return render(request, "custom_admin/booking_view.html", {"booking": booking, "status_form": status_form})


@admin_required
@require_POST
def booking_update_status(request, pk):
    booking = get_object_or_404(Booking.all_objects, pk=pk, is_deleted=False)
    form = BookingStatusForm(request.POST, instance=booking)
    if form.is_valid():
        form.save(update_fields=["status"])
        messages.success(request, "Booking status updated.")
    else:
        messages.error(request, "Invalid status update request.")
    return redirect(request.POST.get("next") or "custom_admin:booking_list")


@admin_required
@require_POST
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking.all_objects, pk=pk, is_deleted=False)
    booking.status = "Rejected"
    booking.save(update_fields=["status"])
    messages.success(request, "Booking canceled successfully.")
    return redirect(request.POST.get("next") or "custom_admin:booking_list")


@admin_required
@require_POST
def booking_delete(request, pk):
    booking = get_object_or_404(Booking.all_objects, pk=pk, is_deleted=False)
    booking.soft_delete(by_user=request.user)
    messages.success(request, "Booking archived successfully.")
    return redirect("custom_admin:booking_list")


@admin_required
@require_POST
def booking_hard_delete(request, pk):
    booking = get_object_or_404(Booking.all_objects, pk=pk, is_deleted=True)
    booking.delete()
    messages.success(request, "Booking permanently deleted.")
    return redirect("custom_admin:booking_list")


@admin_required
def blog_list(request):
    q = request.GET.get("q", "").strip()
    sort = _safe_sort(request.GET.get("sort", "newest"), {"newest", "oldest", "title"}, "newest")
    order_map = {
        "newest": "-created_at",
        "oldest": "created_at",
        "title": "title",
    }

    blogs_qs = BlogPost.objects.select_related("author")
    if q:
        blogs_qs = blogs_qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

    paginator = Paginator(blogs_qs.order_by(order_map[sort]), 10)
    posts = paginator.get_page(request.GET.get("page"))
    return render(request, "custom_admin/blog_list.html", {"posts": posts, "q": q, "sort": sort})


@admin_required
def blog_add(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, "Blog post created.")
            return redirect("custom_admin:blog_list")
    else:
        form = BlogPostForm()
    return render(request, "custom_admin/blog_form.html", {"form": form, "action": "Create"})


@admin_required
def blog_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post updated.")
            return redirect("custom_admin:blog_list")
    else:
        form = BlogPostForm(instance=post)
    return render(request, "custom_admin/blog_form.html", {"form": form, "action": "Edit", "post": post})


@admin_required
@require_POST
def blog_toggle_publish(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.is_published = not post.is_published
    post.save(update_fields=["is_published"])
    state = "published" if post.is_published else "unpublished"
    messages.success(request, f"Blog post {state}.")
    return redirect("custom_admin:blog_list")


@admin_required
@require_POST
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.delete()
    messages.success(request, "Blog post deleted.")
    return redirect("custom_admin:blog_list")


@admin_required
def user_list(request):
    q = request.GET.get("q", "").strip()
    sort = _safe_sort(request.GET.get("sort", "newest"), {"newest", "oldest", "username"}, "newest")
    order_map = {
        "newest": "-id",
        "oldest": "id",
        "username": "user__username",
    }

    users_qs = Profile.objects.select_related("user")
    if q:
        users_qs = users_qs.filter(
            Q(user__username__icontains=q)
            | Q(location__icontains=q)
            | Q(name__icontains=q)
            | Q(user__email__icontains=q)
        )

    paginator = Paginator(users_qs.order_by(order_map[sort]), 20)
    users = paginator.get_page(request.GET.get("page"))
    return render(request, "custom_admin/user_list.html", {"users": users, "q": q, "sort": sort})


@admin_required
def user_view(request, pk):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=pk)
    recent_bookings = (
        Booking.objects.select_related("chef")
        .filter(customer=profile.user)
        .order_by("-date", "-time")[:8]
    )
    return render(request, "custom_admin/user_view.html", {"profile": profile, "recent_bookings": recent_bookings})


@admin_required
def user_edit(request, pk):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=pk)

    if request.method == "POST":
        profile.user.username = request.POST.get("username", profile.user.username).strip()
        profile.user.email = request.POST.get("email", profile.user.email).strip()
        profile.name = request.POST.get("name", profile.name)
        profile.mobile_number = request.POST.get("mobile_number", profile.mobile_number)
        profile.location = request.POST.get("location", profile.location)
        profile.bio = request.POST.get("bio", profile.bio)

        profile.user.save()
        profile.save()
        messages.success(request, "User profile updated.")
        return redirect("custom_admin:user_view", pk=profile.pk)

    return render(request, "custom_admin/user_edit.html", {"profile": profile})


@admin_required
@require_POST
def user_toggle_active(request, pk):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=pk)
    if profile.user == request.user:
        messages.error(request, "You cannot deactivate your own superuser account.")
        return redirect("custom_admin:user_list")

    profile.user.is_active = not profile.user.is_active
    profile.user.save(update_fields=["is_active"])
    state = "activated" if profile.user.is_active else "deactivated"
    messages.success(request, f"User {state} successfully.")
    return redirect("custom_admin:user_list")


@admin_required
@require_POST
def user_delete(request, pk):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=pk)
    if profile.user == request.user:
        messages.error(request, "You cannot delete your own superuser account.")
        return redirect("custom_admin:user_list")

    profile.user.delete()
    messages.success(request, "User deleted.")
    return redirect("custom_admin:user_list")


@admin_required
def contact_query_list(request):
    q = request.GET.get("q", "").strip()
    queries_qs = ContactQuery.objects.filter(is_deleted=False)
    if q:
        queries_qs = queries_qs.filter(
            Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone_number__icontains=q)
            | Q(city__icontains=q)
            | Q(message__icontains=q)
        )
    paginator = Paginator(queries_qs, 20)
    queries = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "custom_admin/contact_query_list.html",
        {"queries": queries, "q": q},
    )


@admin_required
def contact_query_view(request, pk):
    query = get_object_or_404(ContactQuery, pk=pk, is_deleted=False)
    return render(request, "custom_admin/contact_query_view.html", {"query": query})


@admin_required
@require_POST
def contact_query_delete(request, pk):
    query = get_object_or_404(ContactQuery, pk=pk, is_deleted=False)
    query.is_deleted = True
    query.save(update_fields=["is_deleted"])
    messages.success(request, "Contact query deleted successfully.")
    return redirect("custom_admin:contact_query_list")
