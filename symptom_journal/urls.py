"""
Root URL configuration for symptom_journal.

Wires up the landing page, a themed login page (LoginView with our template
and styled form), the accounts app (registration), Django's built-in auth
routes (logout and password views), and the checker/history app routes.
"""
from django.contrib.auth.views import LoginView
from django.urls import include, path

from apps.accounts.forms import StyledAuthenticationForm

from .views import home_view

urlpatterns = [
    path("", home_view, name="home"),
    # Themed login page — must precede the auth include so it wins for /accounts/login/.
    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=StyledAuthenticationForm,
        ),
        name="login",
    ),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("check/", include("apps.checker.urls")),
    path("history/", include("apps.history.urls")),
]
