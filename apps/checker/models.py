"""Database models for the checker app."""
from django.conf import settings
from django.db import models


class SymptomCheck(models.Model):
    """One completed symptom check: input, AI follow-ups, and triage result.

    `user` is nullable so guest checks can complete without saving an owner;
    records are only created for logged-in users. `is_deleted` supports the
    soft delete used by the history timeline (P5).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    symptom_description = models.TextField()
    follow_up_questions = models.JSONField()
    follow_up_answers = models.JSONField(default=dict)
    ai_result = models.JSONField(default=dict)
    language = models.CharField(max_length=10)
    triage_tier = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Readable label for shell/debug output."""
        return f"{self.triage_tier} check on {self.created_at:%Y-%m-%d}"
