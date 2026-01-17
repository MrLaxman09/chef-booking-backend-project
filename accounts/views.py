from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Account created successfully.")
            return redirect('chef_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from booking.models import Booking

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-date', '-time')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

from django.shortcuts import render, get_object_or_404
from .models import Profile

from django.contrib.auth.models import User

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    is_owner = request.user == user
    return render(request, 'accounts/profile_detail.html', {
        'profile': profile,
        'is_owner': is_owner,
        'user': user,
    })



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})


# views.py
from django.forms import modelformset_factory
from .models import WorkImage, Profile
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def upload_work_images(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    WorkImageFormSet = modelformset_factory(WorkImage, fields=('image',), extra=2, can_delete=True)

    if request.method == 'POST':
        formset = WorkImageFormSet(request.POST, request.FILES, queryset=WorkImage.objects.filter(profile=profile))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.profile = profile
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('profile_detail', username=username)
    else:
        formset = WorkImageFormSet(queryset=WorkImage.objects.filter(profile=profile))

    return render(request, 'accounts/upload_work_images.html', {'formset': formset, 'profile': profile})

