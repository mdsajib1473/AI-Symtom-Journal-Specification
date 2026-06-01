"""
URL routes for the history app.

Empty in P1 — the history timeline is built in P5. This module exists so the
project URLconf can `include("apps.history.urls")` without error.
"""
from django.urls import path  # noqa: F401  (used once routes are added in P5)

app_name = "history"

urlpatterns = []
