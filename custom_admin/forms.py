from django import forms
from booking.models import Chef  # change 'app' to your app name

class ChefForm(forms.ModelForm):
    class Meta:
        model = Chef
        fields = ['name', 'specialty', 'experience', 'team_members', 'price_per_person', 'image'] # adjust fields
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control"}),
            "experience": forms.NumberInput(attrs={"class":"form-control"}),
            "price_per_person": forms.NumberInput(attrs={"class":"form-control"}),
            "specialty": forms.TextInput(attrs={"class":"form-control"}),
            "image": forms.ClearableFileInput(attrs={"class":"form-control"}),
        }
