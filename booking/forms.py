from django import forms

from .models import Chef


class ChefForm(forms.ModelForm):
    class Meta:
        model = Chef
        fields = ["name", "specialty", "experience", "team_members", "price_per_person", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = "form-control"
            if isinstance(field.widget, forms.FileInput):
                css_class = "form-control"
            field.widget.attrs.update({"class": css_class})

        self.fields["experience"].widget.attrs.update({"min": 0})
        self.fields["team_members"].widget.attrs.update({"min": 2})
        self.fields["price_per_person"].widget.attrs.update({"min": 0, "step": "0.01"})
