"""Authentication forms for the accounts app."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

# Shared Tailwind classes so login and signup inputs match the design system
# defined in base.html (border #E5E7EB, rounded-lg, teal focus ring).
INPUT_CLASSES = (
    "w-full border border-[#E5E7EB] rounded-lg px-3 py-2 text-ink "
    "focus:outline-none focus:ring-2 focus:ring-[#0F766E] focus:border-[#0F766E]"
)


def apply_input_styling(fields):
    """Attach the shared input CSS class to every field's widget."""
    for field in fields.values():
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} {INPUT_CLASSES}".strip()


class SignUpForm(UserCreationForm):
    """Django's UserCreationForm extended with a required, unique email."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        """Apply design-system styling to every field."""
        super().__init__(*args, **kwargs)
        apply_input_styling(self.fields)

    def clean_email(self):
        """Reject an email address that is already registered."""
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        """Save the new user, persisting the validated email address."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class StyledAuthenticationForm(AuthenticationForm):
    """Login form styled to match the design system."""

    def __init__(self, *args, **kwargs):
        """Apply design-system styling to every field."""
        super().__init__(*args, **kwargs)
        apply_input_styling(self.fields)
