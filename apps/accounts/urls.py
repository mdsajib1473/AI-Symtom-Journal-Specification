"""URL routes for the accounts app (registration)."""
from django.urls import path

from .views import signup_view

# No app_name namespace: the name "signup" is referenced unqualified as
# {% url 'signup' %} in base.html, which P1 already wired up.
urlpatterns = [
    path("signup/", signup_view, name="signup"),
]
