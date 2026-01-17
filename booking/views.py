from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Chef, Booking
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import Profile


def home(request):
    return render(request, 'booking/home.html')
def about(request):
    return render(request, 'booking/about.html')
# def blog(request):
#     return render(request, 'booking/blog.html')

from django.shortcuts import render
from .models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'booking/blog_list.html', {'posts': posts})

def blog_detail(request, pk):
    post = BlogPost.objects.get(pk=pk)
    return render(request, 'booking/blog_detail.html', {'post': post})


# def dashboard(request):
#     return render(request, 'booking/dashboard.html')

@login_required
def chef_list(request):
    query = request.GET.get('q')  # search bar ka input
    profiles = Profile.objects.all()
    chefs = Chef.objects.all()
    if query:
        chefs = chefs.filter(
        Q(name__icontains=query) |
        Q(specialty__icontains=query) |
        Q(experience__icontains=query)
    )

    return render(request, 'booking/chef_list.html', {
    'chefs': chefs,
    'profiles': profiles
})

@login_required
def dashboard(request):
    # Logged in chef ke bookings
    cos_bookings = Booking.objects.filter(customer=request.user)
    chefs = Chef.objects.all()
    bookings = Booking.objects.filter(chef__user=request.user)
    pending_count = bookings.filter(status="Pending").count()
    return render(request, 'booking/dashboard.html', {'bookings': bookings,  'chefs': chefs, 'cos_bookings': cos_bookings, "pending_count": pending_count })



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)

    # Sirf wahi chef jiska booking hai, update kar sake
    if request.user != booking.chef.user:
        messages.error(request, "You are not allowed to update this booking!")
        return redirect('view_bookings')

    booking.status = status
    booking.save()
    messages.success(request, f"Booking {status.lower()} successfully.")
    return redirect('view_bookings')


@login_required
def book_chef(request, chef_id):
    chef = get_object_or_404(Chef, id=chef_id)
    if request.method == 'POST':
        date = request.POST['date']
        time = request.POST['time']
        person = int(request.POST['person'])
        total_price = chef.price_per_person * person

        Booking.objects.create(
            customer=request.user,
            chef=chef,
            date=date,
            time=time,
            person=person,
            total_price=total_price,
            status='Pending'
        )
        return redirect('chef_list')
    return render(request, 'booking/book_chef.html', {'chef': chef})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Chef
from .forms import ChefForm

@login_required
def become_chef(request):
    # Agar user already chef hai to redirect
    if Chef.objects.filter(user=request.user).exists():
        return redirect('chef_list')
    
    if request.method == 'POST':
        form = ChefForm(request.POST, request.FILES)
        if form.is_valid():
            chef = form.save(commit=False)
            chef.user = request.user
            chef.save()
            return redirect('chef_list')
    else:
        form = ChefForm()
    
    return render(request, 'booking/become_chef.html', {'form': form})



# booking/views.py
from django.contrib.auth.decorators import login_required
from .models import Booking




def navbar_view(request):
    chef = Chef.objects.filter(user=request.user).first()
    return render(request, 'base.html', {'chef': chef})

@login_required
def user_profile(request):
    profile = Profile.objects.filter(user=request.user).first()
    chef = Chef.objects.filter(user=request.user).first()
    return render(request, 'base.html', {
    'chef': chef,
    'profiles': profile
})