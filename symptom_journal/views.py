"""
Project-level views for symptom_journal.

Intentionally minimal in P1:
  * home_view   — renders the public landing page.
  * signup_view — placeholder until real registration is built in P2 (auth).
"""
from django.http import HttpResponse
from django.shortcuts import render


def home_view(request):
    """Render the public landing page."""
    return render(request, "home.html")


def signup_view(request):
    """Placeholder sign-up view. Real registration arrives in P2 (auth)."""
    return HttpResponse(
        "Sign up is coming in P2. (Placeholder view.)",
        content_type="text/plain; charset=utf-8",
    )
