from django import forms

from .models import Chef, ContactQuery


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


class ContactQueryForm(forms.ModelForm):
    class Meta:
        model = ContactQuery
        fields = ["name", "email", "phone_number", "address", "city", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your full name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "you@example.com"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone number"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Street address"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Tell us what kind of chef support you need.",
                }
            ),
        }
        help_texts = {
            "phone_number": "Include country code if available.",
        }

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        if not value:
            return value

        normalized = value.replace(" ", "").replace("-", "")
        if normalized.startswith("+"):
            normalized = normalized[1:]
        if not normalized.isdigit() or not (10 <= len(normalized) <= 15):
            raise forms.ValidationError("Enter a valid phone number with 10 to 15 digits.")
        return value
