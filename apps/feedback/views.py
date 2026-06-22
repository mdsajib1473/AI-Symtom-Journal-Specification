"""View for submitting participant feedback on a triage result."""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.checker.models import SymptomCheck

from .models import Feedback

MAX_COMMENT_LENGTH = 500


@require_POST
def submit_feedback_view(request, check_pk):
    """Save one Feedback for a symptom check, guarding against duplicates.

    Both ratings must be integers in 1..5; the comment is optional and capped
    at 500 characters. A check that already has feedback redirects silently so
    a result can only be rated once. On success a thank-you message is shown
    and the user returns to /check/. Invalid input re-renders the result page
    so the participant can correct it.
    """
    check = SymptomCheck.objects.filter(pk=check_pk).first()

    # One rating per check: silently ignore any repeat submission.
    if Feedback.objects.filter(symptom_check_id=check_pk).exists():
        return redirect("checker:symptom_form")

    usefulness = _parse_rating(request.POST.get("usefulness"))
    language_quality = _parse_rating(request.POST.get("language_quality"))
    comments = request.POST.get("comments", "").strip()

    if usefulness is None or language_quality is None or len(comments) > MAX_COMMENT_LENGTH:
        return render(
            request,
            "checker/result.html",
            {
                "result": check.ai_result if check else {},
                "language": check.language if check else "English",
                "check_pk": check_pk,
                "feedback_submitted": False,
                "feedback_error": True,
            },
        )

    Feedback.objects.create(
        symptom_check=check,
        usefulness=usefulness,
        language_quality=language_quality,
        comments=comments,
    )
    messages.success(request, "Thank you for your feedback!")
    return redirect("checker:symptom_form")


def _parse_rating(value):
    """Return an int in 1..5 from raw POST data, or None if out of range/invalid."""
    try:
        rating = int(value)
    except (TypeError, ValueError):
        return None
    return rating if 1 <= rating <= 5 else None
