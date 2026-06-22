"""URL routes for the checker app - the three-step symptom check flow."""
from django.urls import path

from .views import (
    get_questions_view,
    get_result_view,
    symptom_form_view,
    view_result_view,
)

app_name = "checker"

urlpatterns = [
    path("", symptom_form_view, name="symptom_form"),
    path("questions/", get_questions_view, name="get_questions"),
    path("result/", get_result_view, name="get_result"),
    path("result/<int:pk>/", view_result_view, name="view_result"),
]
