"""
Root URL configuration for symptom_journal.

P1 wires up the landing page, Django's built-in auth routes, a placeholder
signup view, and the (currently empty) checker/history app routes so the
project boots cleanly before those features are built in later steps.
"""
from django.urls import include, path

from .views import home_view, signup_view

urlpatterns = [
    path("", home_view, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", signup_view, name="signup"),  # placeholder (P2)
    path("check/", include("apps.checker.urls")),
    path("history/", include("apps.history.urls")),
]
