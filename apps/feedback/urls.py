"""URL routes for the feedback app."""
from django.urls import path

from .views import submit_feedback_view

app_name = "feedback"

urlpatterns = [
    path("submit/<int:check_pk>/", submit_feedback_view, name="submit_feedback"),
]
