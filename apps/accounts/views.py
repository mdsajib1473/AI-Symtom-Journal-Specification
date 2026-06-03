"""Views for the accounts app: user registration."""
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup_view(request):
    """Register a new user, log them in, and redirect to the symptom checker.

    Already-authenticated users are sent straight to the checker instead of
    being shown the registration form again.
    """
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})
