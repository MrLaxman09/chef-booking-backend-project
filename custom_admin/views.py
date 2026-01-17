from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from booking.models import Chef, Booking
from accounts.models import Profile # change 'app' to your app
from .forms import ChefForm
from django.contrib.auth.models import User
# helper: only staff allowed
def staff_required(user):
    return user.is_authenticated and user.is_staff

def user_edit(request, user_id):
    user = User.objects.get(id=user_id)
    profile = user.profile

    if request.method == "POST":
        user.username = request.POST["username"]
        user.email = request.POST["email"]
        profile.name = request.POST["name"]
        profile.mobile = request.POST["mobile"]
        profile.role = request.POST["role"]
        profile.status = request.POST["status"]
        profile.bio = request.POST["bio"]

        user.save()
        profile.save()

        return redirect("admin_user_list")

    return render(request, "custom_admin/user_edit.html", {"user": user})


# Dashboard
@user_passes_test(staff_required, login_url="login")
def dashboard(request):
    chefs = Chef.objects.count()
    bookings = Booking.objects.count()
    users = Profile.objects.count()
    # recent_bookings = Booking.objects.order_by("-created_at")[:6]
    context = {
        "chefs_count": chefs,
        "bookings_count": bookings,
        "users_count": users,
        # "recent_bookings": recent_bookings,
    }
    return render(request, "custom_admin/dashboard.html", context)


# ----- Chef CRUD -----
@user_passes_test(staff_required, login_url="login")
def chef_list(request):
    q = request.GET.get("q", "")
    chefs = Chef.objects.all()
    if q:
        chefs = chefs.filter(Q(name__icontains=q) | Q(speciality__icontains=q))
    paginator = Paginator(chefs.order_by("-id"), 12)
    page = request.GET.get("page")
    chefs = paginator.get_page(page)
    return render(request, "custom_admin/chef_list.html", {"chefs": chefs, "q": q})

@user_passes_test(staff_required, login_url="login")
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

@user_passes_test(staff_required, login_url="login")
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

@user_passes_test(staff_required, login_url="login")
def chef_delete(request, pk):
    chef = get_object_or_404(Chef, pk=pk)
    if request.method == "POST":
        chef.delete()
        messages.success(request, "Chef deleted.")
        return redirect("custom_admin:chef_list")
    return render(request, "custom_admin/chef_confirm_delete.html", {"chef": chef})


# ----- Bookings -----
@user_passes_test(staff_required, login_url="login")
def booking_list(request):
    q = request.GET.get("q", "")
    bookings = Booking.objects.select_related("customer", "chef").all()
    if q:
        bookings = bookings.filter(Q(customer__username__icontains=q) | Q(chef__name__icontains=q))
    paginator = Paginator(bookings.order_by("-date"), 15)
    bookings = paginator.get_page(request.GET.get("page"))
    return render(request, "custom_admin/booking_list.html", {"bookings": bookings, "q": q})

@user_passes_test(staff_required, login_url="login")
def booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, "custom_admin/booking_view.html", {"booking": booking})

@user_passes_test(staff_required, login_url="login")
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking removed.")
        return redirect("custom_admin:booking_list")
    return render(request, "custom_admin/booking_confirm_delete.html", {"booking": booking})


# ----- Users -----
@user_passes_test(staff_required, login_url="login")
def user_list(request):
    q = request.GET.get("q", "")
    users = Profile.objects.select_related("user").all()
    if q:
        users = users.filter(Q(user__username__icontains=q) | Q(location__icontains=q))
    paginator = Paginator(users.order_by("-id"), 20)
    users = paginator.get_page(request.GET.get("page"))
    return render(request, "custom_admin/user_list.html", {"users": users, "q": q})

@user_passes_test(staff_required, login_url="login")
def user_view(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, "custom_admin/user_view.html", {"profile": profile})

def user_delete(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        user.delete()
        return redirect("admin_user_list")

    return render(request, "custom_admin/user_delete.html", {"user": user})
