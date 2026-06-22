"""Database model for participant feedback on a triage result."""
from django.db import models


class Feedback(models.Model):
    """One participant's rating of a single symptom check result.

    Linked one-to-one to the SymptomCheck it rates. The link is nullable so a
    rating can exist without a saved check; in practice every check is now
    persisted, and the OneToOne relation plus the view's duplicate guard keep
    it to a single Feedback per check.
    """

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    symptom_check = models.OneToOneField(
        "checker.SymptomCheck",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="feedback",
    )
    usefulness = models.IntegerField(choices=RATING_CHOICES)
    language_quality = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Readable label for shell/admin output."""
        return f"Feedback (useful={self.usefulness}, language={self.language_quality})"
