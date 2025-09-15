from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label
            })


from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'profile_image', 'experience', 'location',
            'mobile_number', 'bio', 'education', 'dishes'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from .models import WorkImage

class WorkImageForm(forms.ModelForm):
    class Meta:
        model = WorkImage
        fields = ['image']
        extra=5
        widgets = {
            'image': forms.FileInput(),
        }
