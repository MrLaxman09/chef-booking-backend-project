from django import forms
from .models import Chef

class ChefForm(forms.ModelForm):
    class Meta:
        model = Chef
        fields = ['name', 'specialty', 'experience', 'team_members', 'price_per_person', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
