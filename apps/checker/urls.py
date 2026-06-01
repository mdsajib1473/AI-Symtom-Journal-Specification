"""
URL routes for the checker app.

Empty in P1 — the symptom-check form and views are built in P3. This module
exists so the project URLconf can `include("apps.checker.urls")` without error.
"""
from django.urls import path  # noqa: F401  (used once routes are added in P3)

app_name = "checker"

urlpatterns = []
