from django import forms
from .models import Review, ChefResponse

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class ChefResponseForm(forms.ModelForm):
    class Meta:
        model = ChefResponse
        fields = ['response']
        widgets = {
            'response': forms.Textarea(attrs={'rows': 3}),
        }
