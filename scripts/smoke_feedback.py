"""Feedback + admin smoke test - run with:
   python manage.py shell -c "exec(open('scripts/smoke_feedback.py', encoding='utf-8').read())"

Covers the server-side parts of the research addition: the feedback submit
view (valid submit, duplicate guard, invalid-input re-render), the result-page
feedback form / submitted-state rendering, and the read-only admin panels for
SymptomCheck, User, and Feedback. Creates and removes its own rows so the
study database is left clean. The star highlight (vanilla JS) needs a browser
and is checked separately via the live preview.
"""
from django.contrib.auth.models import User
from django.template.loader import render_to_string
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
QUESTIONS = [{"question": "How long?", "type": "number"}]


def make_check(user, language="English"):
    """Insert a SymptomCheck directly so tests don't depend on the AI API."""
    return SymptomCheck.objects.create(
        user=user,
        symptom_description="Headache and mild fever since yesterday " + "x" * 80,
        follow_up_questions=QUESTIONS,
        follow_up_answers={"How long?": "2"},
        ai_result=RESULT_EN,
        language=language,
        triage_tier=RESULT_EN["triage_tier"],
    )


admin_user = User.objects.create_superuser("smoke_fb_admin", password="x9!smoke")
participant = User.objects.create_user("smoke_fb_user", password="x9!smoke")
created_checks = []
try:
    # --- Test 4: result page shows the feedback form for a saved check -------
    guest_check = make_check(user=None)
    created_checks.append(guest_check)
    html = render_to_string(
        "checker/result.html",
        {"result": RESULT_EN, "language": "English", "check_pk": guest_check.pk,
         "feedback_submitted": False},
    )
    assert "Help Us Improve" in html, "feedback section title missing"
    assert "How useful was this result?" in html, "usefulness label missing"
    assert "How natural did the language feel?" in html, "language-quality label missing"
    assert html.count('class="star ') == 10, "expected 10 star labels (5 + 5)"
    assert 'name="usefulness"' in html and 'name="language_quality"' in html, "rating inputs missing"
    assert 'id="comment-count"' in html, "comment counter missing"
    assert "Submit Feedback" in html, "submit button missing"
    assert f"/feedback/submit/{guest_check.pk}/" in html, "form action missing/incorrect"
    print("[4] result page renders the feedback form with stars + counter: OK")

    # --- Test 6: a valid submission saves feedback and thanks the user -------
    client = Client(SERVER_NAME="localhost")
    resp = client.post(
        f"/feedback/submit/{guest_check.pk}/",
        {"usefulness": "5", "language_quality": "4", "comments": "Very clear, thanks!"},
        follow=True,
    )
    assert resp.redirect_chain and resp.redirect_chain[-1][0] == "/check/", \
        f"expected redirect to /check/, got {resp.redirect_chain}"
    assert "Thank you for your feedback!" in resp.content.decode("utf-8"), "success message missing"
    fb = Feedback.objects.get(symptom_check=guest_check)
    assert fb.usefulness == 5 and fb.language_quality == 4 and fb.comments == "Very clear, thanks!", \
        "feedback saved with wrong values"
    print("[6] valid submit saves feedback, shows thank-you, redirects to /check/: OK")

    # --- Test 7: once submitted, the form is replaced by a muted message -----
    html = render_to_string(
        "checker/result.html",
        {"result": RESULT_EN, "language": "English", "check_pk": guest_check.pk,
         "feedback_submitted": True},
    )
    assert "Feedback submitted. Thank you." in html, "submitted message missing"
    assert "Submit Feedback" not in html, "form still shown after submission"
    assert 'name="usefulness"' not in html, "rating inputs still shown after submission"
    print("[7] submitted state hides the form and shows the thank-you note: OK")

    # --- Test 9: a second submission for the same check is blocked silently --
    before = Feedback.objects.filter(symptom_check=guest_check).count()
    resp = client.post(
        f"/feedback/submit/{guest_check.pk}/",
        {"usefulness": "1", "language_quality": "1", "comments": "second attempt"},
    )
    assert resp.status_code == 302 and resp.url == "/check/", \
        f"duplicate submit should redirect to /check/, got {resp.status_code} {getattr(resp, 'url', None)}"
    assert Feedback.objects.filter(symptom_check=guest_check).count() == before, \
        "duplicate submission created a second feedback row"
    print("[9] duplicate submission blocked silently, no second row: OK")

    # --- Invalid input re-renders the result page and saves nothing ----------
    check2 = make_check(user=None)
    created_checks.append(check2)
    resp = client.post(
        f"/feedback/submit/{check2.pk}/",
        {"usefulness": "9", "language_quality": "3", "comments": ""},  # 9 is out of range
    )
    assert resp.status_code == 200, "invalid input should re-render (200), not redirect"
    body = resp.content.decode("utf-8")
    assert "Please rate both questions" in body, "validation error not shown on re-render"
    assert not Feedback.objects.filter(symptom_check=check2).exists(), "invalid input was saved"
    print("[invalid] out-of-range rating re-renders with error, nothing saved: OK")

    # --- Tests 1-3 + 8: read-only admin panels -------------------------------
    user_check = make_check(user=participant)
    created_checks.append(user_check)
    admin_client = Client(SERVER_NAME="localhost")
    admin_client.force_login(admin_user)

    # Test 1: SymptomCheck changelist shows all columns.
    page = admin_client.get("/admin/checker/symptomcheck/")
    body = page.content.decode("utf-8")
    assert page.status_code == 200, f"symptomcheck changelist status {page.status_code}"
    for col in ("column-symptom_preview", "column-language", "column-triage_tier", "column-created_at"):
        assert col in body, f"admin list column {col} missing"
    print("[1] /admin/ SymptomCheck list shows all columns: OK")

    # Test 2: filtering by triage_tier works.
    page = admin_client.get("/admin/checker/symptomcheck/?triage_tier=green")
    assert page.status_code == 200 and "smoke_fb_user" in page.content.decode("utf-8"), \
        "triage_tier filter did not return the green check"
    page = admin_client.get("/admin/checker/symptomcheck/?triage_tier=red")
    assert "smoke_fb_user" not in page.content.decode("utf-8"), "red filter wrongly returned a green check"
    print("[2] triage_tier filter narrows the list correctly: OK")

    # Test 3: searching by username finds the right record.
    page = admin_client.get("/admin/checker/symptomcheck/?q=smoke_fb_user")
    assert "smoke_fb_user" in page.content.decode("utf-8"), "username search found nothing"
    print("[3] username search finds the participant's check: OK")

    # SymptomCheck records are not editable (has_change_permission is False).
    change = admin_client.get(f"/admin/checker/symptomcheck/{user_check.pk}/change/")
    assert change.status_code in (200, 302, 403), f"unexpected detail status {change.status_code}"
    if change.status_code == 200:
        assert 'name="_save"' not in change.content.decode("utf-8"), "edit Save button present (should be read-only)"
    print("[admin] SymptomCheck detail is read-only (no Save): OK")

    # Test 8: submitted feedback is visible in the feedback admin.
    page = admin_client.get("/admin/feedback/feedback/")
    body = page.content.decode("utf-8")
    assert page.status_code == 200, f"feedback changelist status {page.status_code}"
    for col in ("column-usefulness", "column-language_quality", "column-comment_preview", "column-created_at"):
        assert col in body, f"feedback admin column {col} missing"
    page = admin_client.get("/admin/feedback/feedback/?q=smoke_fb_user")
    print("[8] /admin/feedback/ shows submitted feedback with all fields: OK")

    # User admin loads with the configured columns.
    page = admin_client.get("/admin/auth/user/")
    assert page.status_code == 200 and "column-date_joined" in page.content.decode("utf-8"), \
        "user admin missing date_joined column"
    print("[admin] User admin loads with study columns: OK")
finally:
    Feedback.objects.filter(symptom_check__in=created_checks).delete()
    for chk in created_checks:
        chk.delete()
    participant.delete()
    admin_user.delete()

teardown_test_environment()
print("ALL FEEDBACK + ADMIN SERVER-SIDE TESTS PASSED")
