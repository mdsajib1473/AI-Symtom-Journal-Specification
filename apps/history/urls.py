"""URL routes for the history app — timeline and soft delete."""
from django.urls import path

from .views import delete_check_view, history_list_view

app_name = "history"

urlpatterns = [
    path("", history_list_view, name="history_list"),
    path("delete/<int:pk>/", delete_check_view, name="delete_check"),
]
