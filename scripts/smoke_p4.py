"""P4 smoke test — run with: python manage.py shell -c "exec(open('scripts/smoke_p4.py', encoding='utf-8').read())"

Covers the server-side P4 checks: login gate, timeline rendering with
language-aware labels, soft delete + ownership 403, empty state, and the
Bangla disclaimer fix on the result page. Creates and removes its own users.
JS-only behaviours (expand/collapse, modal) need a browser and are not
covered here.
"""
from django.contrib.auth.models import User
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment

from apps.checker.models import SymptomCheck

setup_test_environment()

DISCLAIMER = "This is not a medical diagnosis. Consult a qualified doctor."
BN_DISCLAIMER = "এটি কোনো চিকিৎসা রোগ নির্ণয় নয়। একজন যোগ্য ডাক্তারের পরামর্শ নিন।"

RESULT_EN = {
    "possible_conditions": [{"name": "Tension headache", "description": "Often stress-related."}],
    "triage_tier": "green",
    "recommended_action": "Rest and hydrate.",
    "warning_signs": ["Pain becomes severe"],
    "disclaimer": DISCLAIMER,
}
RESULT_BN = {
    "possible_conditions": [{"name": "মাইগ্রেন", "description": "তীব্র মাথা ব্যথা।"}],
    "triage_tier": "red",
    "recommended_action": "দ্রুত হাসপাতালে যান।",
    "warning_signs": ["জ্ঞান হারানো"],
    "disclaimer": DISCLAIMER,
}
QUESTIONS = [{"question": "How long?", "type": "number"}]


def make_check(user, description, language, result):
    """Insert a SymptomCheck directly so tests don't depend on the AI API."""
    return SymptomCheck.objects.create(
        user=user,
        symptom_description=description,
        follow_up_questions=QUESTIONS,
        follow_up_answers={"How long?": "2"},
        ai_result=result,
        language=language,
        triage_tier=result["triage_tier"],
    )


# --- Test 1: guest is redirected to login ------------------------------------
guest = Client(SERVER_NAME="localhost")
resp = guest.get("/history/")
assert resp.status_code == 302 and resp.url.startswith("/accounts/login/"), \
    f"guest got {resp.status_code} -> {getattr(resp, 'url', None)}"
print("[1] guest /history/ redirects to login: OK")

owner = User.objects.create_user("smoke_p4_owner", password="x9!smoke")
other = User.objects.create_user("smoke_p4_other", password="x9!smoke")
try:
    en_check = make_check(owner, "Headache and mild fever since yesterday " + "x" * 100, "English", RESULT_EN)
    bn_check = make_check(owner, "গতকাল থেকে মাথা ব্যথা", "Bangla", RESULT_BN)
    other_check = make_check(other, "Sore throat", "English", RESULT_EN)

    client = Client(SERVER_NAME="localhost")
    client.force_login(owner)

    # --- Tests 2+3: timeline shows own entries with language-aware labels ----
    html = client.get("/history/").content.decode("utf-8")
    assert "Rest at Home" in html, "EN green badge label missing"
    assert "জরুরি চিকিৎসা নিন" in html, "BN red badge label missing"
    assert "Possible Conditions" in html and "সম্ভাব্য সমস্যা" in html, "detail headings missing"
    assert BN_DISCLAIMER in html and DISCLAIMER in html, "disclaimers missing"
    assert "Sore throat" not in html, "another user's entry leaked into timeline"
    assert html.count("delete-btn") >= 2, "delete buttons missing"
    print("[2,3] timeline renders both entries with correct-language labels: OK")

    # --- Ownership: deleting someone else's record is forbidden --------------
    resp = client.post(f"/history/delete/{other_check.pk}/")
    assert resp.status_code == 403, f"expected 403, got {resp.status_code}"
    other_check.refresh_from_db()
    assert other_check.is_deleted is False
    print("[403] cannot delete another user's entry: OK")

    # --- Test 8: soft delete own entry, success message shown ----------------
    resp = client.post(f"/history/delete/{en_check.pk}/", follow=True)
    html = resp.content.decode("utf-8")
    assert "Entry deleted successfully." in html, "success message missing"
    en_check.refresh_from_db()
    assert en_check.is_deleted is True, "record was not soft-deleted"
    assert "Rest at Home" not in html, "deleted entry still on timeline"
    print("[8] delete soft-deletes, shows message, removes from timeline: OK")

    # --- Test 9: empty state after deleting everything ------------------------
    client.post(f"/history/delete/{bn_check.pk}/")
    html = client.get("/history/").content.decode("utf-8")
    assert "No checks yet." in html and "/check/" in html, "empty state missing"
    print("[9] empty state with CTA: OK")

    # --- Test 10: real Bangla check shows Bangla disclaimer on result page ---
    resp = client.post("/check/questions/", {"symptom_text": "গতকাল থেকে আমার মাথা ব্যথা এবং জ্বর আছে।"})
    answers = {
        f"answer_{i}": ("Yes" if q["type"] == "yesno" else "2" if q["type"] == "number" else "না")
        for i, q in enumerate(resp.context["questions"], start=1)
    }
    html = client.post("/check/result/", answers).content.decode("utf-8")
    assert BN_DISCLAIMER in html, "result page disclaimer not in Bangla"
    print("[10] Bangla check result page shows Bangla disclaimer: OK")
finally:
    SymptomCheck.objects.filter(user__in=[owner, other]).delete()
    owner.delete()
    other.delete()

teardown_test_environment()
print("ALL P4 SERVER-SIDE TESTS PASSED")
