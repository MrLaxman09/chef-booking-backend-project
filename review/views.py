from django.shortcuts import render, get_object_or_404, redirect
from .models import Booking, Review, ChefResponse
from .forms import ReviewForm, ChefResponseForm
from django.contrib.auth.decorators import login_required

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if hasattr(booking, 'review'):
        return redirect('view_review', review_id=booking.review.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            return redirect('view_review', review_id=review.id)
    else:
        form = ReviewForm()
    return render(request, 'reviews/submit_review.html', {'form': form})

@login_required
def view_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    response_form = None
    if request.user == review.chef().user:  # assuming Chef has a user field
        if not hasattr(review, 'chefresponse'):
            if request.method == 'POST':
                response_form = ChefResponseForm(request.POST)
                if response_form.is_valid():
                    chef_response = response_form.save(commit=False)
                    chef_response.review = review
                    chef_response.save()
            else:
                response_form = ChefResponseForm()
    return render(request, 'reviews/view_review.html', {'review': review, 'response_form': response_form})
