"""Admin registration for participant feedback (read-only study data)."""
from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Read-only admin view of submitted feedback for the user study."""

    list_display = (
        "symptom_check",
        "usefulness",
        "language_quality",
        "created_at",
        "comment_preview",
    )
    list_filter = ("usefulness", "language_quality", "created_at")
    search_fields = ("symptom_check__user__username", "comments")
    ordering = ("-created_at",)
    readonly_fields = (
        "symptom_check",
        "usefulness",
        "language_quality",
        "comments",
        "created_at",
    )

    @admin.display(description="Comment")
    def comment_preview(self, obj):
        """First 60 characters of the comment for the list view."""
        text = obj.comments or ""
        return text[:60] + ("..." if len(text) > 60 else "")
