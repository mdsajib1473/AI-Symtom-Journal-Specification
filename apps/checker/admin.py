"""Admin registration for the checker app (read-only audit of symptom checks)."""
from django.contrib import admin

from .models import SymptomCheck


@admin.register(SymptomCheck)
class SymptomCheckAdmin(admin.ModelAdmin):
    """Read-only admin view of completed symptom checks for the user study."""

    list_display = ("user", "symptom_preview", "language", "triage_tier", "created_at")
    list_filter = ("triage_tier", "language", "created_at")
    search_fields = ("user__username", "symptom_description")
    ordering = ("-created_at",)
    readonly_fields = (
        "user",
        "symptom_description",
        "follow_up_questions",
        "follow_up_answers",
        "ai_result",
        "language",
        "triage_tier",
        "created_at",
    )

    @admin.display(description="Symptom")
    def symptom_preview(self, obj):
        """First 60 characters of the symptom description for the list view."""
        text = obj.symptom_description
        return text[:60] + ("..." if len(text) > 60 else "")

    def has_change_permission(self, request, obj=None):
        """Symptom records are immutable in the admin (view only, no edits)."""
        return False
