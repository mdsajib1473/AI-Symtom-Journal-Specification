"""Past-result view smoke test - run with:
   python manage.py shell -c "exec(open('scripts/smoke_view_result.py', encoding='utf-8').read())"

Verifies the read-only /check/result/<pk>/ view: login required, owner-only
access (403 for others), 404 for deleted checks, and the feedback section
showing the submitted note or the rating form based on whether the check has
been rated. Creates and removes its own rows.
"""
from django.contrib.auth.models import User
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment

from apps.checker.models import SymptomCheck
from apps.feedback.models import Feedback

setup_test_environment()

RESULT_EN = {
    "possible_conditions": [{"name": "Tension headache", "description": "Often stress-related."}],
    "triage_tier": "green",
    "recommended_action": "Rest and hydrate.",
    "warning_signs": ["Pain becomes severe"],
    "disclaimer": "This is not a medical diagnosis. Consult a qualified doctor.",
}


def make_check(user, is_deleted=False):
    """Insert a SymptomCheck directly so tests don't depend on the AI API."""
    return SymptomCheck.objects.create(
        user=user,
        symptom_description="Headache and mild fever since yesterday " + "x" * 80,
        follow_up_questions=[{"question": "How long?", "type": "number"}],
        follow_up_answers={"How long?": "2"},
        ai_result=RESULT_EN,
        language="English",
        triage_tier="green",
        is_deleted=is_deleted,
    )


owner = User.objects.create_user("smoke_vr_owner", password="x9!smoke")
other = User.objects.create_user("smoke_vr_other", password="x9!smoke")
try:
    rated = make_check(owner)
    Feedback.objects.create(symptom_check=rated, usefulness=4, language_quality=5, comments="Clear.")
    unrated = make_check(owner)
    deleted = make_check(owner, is_deleted=True)
    foreign = make_check(other)

    # Guest is redirected to login.
    guest = Client(SERVER_NAME="localhost")
    resp = guest.get(f"/check/result/{rated.pk}/")
    assert resp.status_code == 302 and resp.url.startswith("/accounts/login/"), \
        f"guest should be redirected to login, got {resp.status_code} {getattr(resp, 'url', None)}"
    print("[guest] /check/result/<pk>/ redirects to login: OK")

    client = Client(SERVER_NAME="localhost")
    client.force_login(owner)

    # Owner viewing a rated check sees the submitted note, not the form.
    body = client.get(f"/check/result/{rated.pk}/").content.decode("utf-8")
    assert "Feedback submitted. Thank you." in body, "submitted note missing on rated check"
    assert "Submit Feedback" not in body, "rating form shown for an already-rated check"
    print("[owner] rated check shows the submitted note (read-only): OK")

    # Owner viewing an unrated check sees the rating form.
    body = client.get(f"/check/result/{unrated.pk}/").content.decode("utf-8")
    assert "Submit Feedback" in body and f"/feedback/submit/{unrated.pk}/" in body, \
        "rating form missing on an unrated check"
    print("[owner] unrated check shows the rating form: OK")

    # Deleted checks are not viewable.
    assert client.get(f"/check/result/{deleted.pk}/").status_code == 404, \
        "deleted check should 404"
    print("[owner] deleted check returns 404: OK")

    # A user cannot view someone else's result.
    assert client.get(f"/check/result/{foreign.pk}/").status_code == 403, \
        "viewing another user's check should be 403"
    print("[owner] another user's check returns 403: OK")

    # The history page links to the new view.
    history = client.get("/history/").content.decode("utf-8")
    assert f"/check/result/{rated.pk}/" in history, "history page missing link to the result view"
    print("[history] timeline links to the full result page: OK")
finally:
    SymptomCheck.objects.filter(user__in=[owner, other]).delete()
    owner.delete()
    other.delete()

teardown_test_environment()
print("ALL PAST-RESULT VIEW TESTS PASSED")
