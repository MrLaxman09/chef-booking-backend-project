from django import forms

from booking.models import BlogPost, Booking, Chef


class ChefForm(forms.ModelForm):
    class Meta:
        model = Chef
        fields = [
            "user",
            "name",
            "specialty",
            "experience",
            "team_members",
            "price_per_person",
            "image",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "specialty": forms.TextInput(attrs={"class": "form-control"}),
            "experience": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "team_members": forms.NumberInput(attrs={"class": "form-control", "min": 2}),
            "price_per_person": forms.NumberInput(attrs={"class": "form-control", "min": 0, "step": "0.01"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "image", "content", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }
