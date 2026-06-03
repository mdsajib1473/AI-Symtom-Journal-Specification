"""Project-level views for symptom_journal."""
from django.shortcuts import render


def home_view(request):
    """Render the public landing page."""
    return render(request, "home.html")
