from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, WorkImage


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": field.label,
                    "autocomplete": "new-password" if "password" in name else "on",
                }
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "name",
            "profile_image",
            "experience",
            "location",
            "mobile_number",
            "bio",
            "education",
            "dishes",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "profile_image": forms.FileInput(attrs={"class": "form-control"}),
            "experience": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "mobile_number": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "education": forms.TextInput(attrs={"class": "form-control"}),
            "dishes": forms.TextInput(attrs={"class": "form-control"}),
        }


class WorkImageForm(forms.ModelForm):
    class Meta:
        model = WorkImage
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }
