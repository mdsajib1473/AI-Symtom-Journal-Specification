"""P3 smoke test — run with: python manage.py shell -c "exec(open('scripts/smoke_p3.py', encoding='utf-8').read())"

Exercises the three-step checker flow with Django's test client, as both a
guest and a logged-in user, and verifies the DB-save behaviour for each.
Creates and removes its own throwaway user.
"""
from django.contrib.auth.models import User
from django.test import Client
from django.test.utils import setup_test_environment, teardown_test_environment

from apps.checker.models import SymptomCheck

# Instrument template rendering so resp.context works outside a test runner.
setup_test_environment()

SYMPTOM_EN = "I have a headache and fever since yesterday morning."
SYMPTOM_BN = "গতকাল থেকে আমার মাথা ব্যথা এবং জ্বর আছে।"


def run_flow(client, symptom, label):
    """Drive form → questions → result and report what came back."""
    resp = client.get("/check/")
    assert resp.status_code == 200, f"GET /check/ -> {resp.status_code}"

    resp = client.post("/check/questions/", {"symptom_text": symptom})
    assert resp.status_code == 200, f"POST questions -> {resp.status_code}"
    questions = resp.context["questions"]
    print(f"[{label}] {len(questions)} questions, first: {questions[0]['question'][:60]}")

    answers = {
        f"answer_{i}": ("Yes" if q["type"] == "yesno" else "2" if q["type"] == "number" else "none")
        for i, q in enumerate(questions, start=1)
    }
    resp = client.post("/check/result/", answers)
    assert resp.status_code == 200, f"POST result -> {resp.status_code}"
    result = resp.context["result"]
    print(f"[{label}] tier={result['triage_tier']}, "
          f"conditions={len(result['possible_conditions'])}, "
          f"disclaimer ok={result['disclaimer'] == 'This is not a medical diagnosis. Consult a qualified doctor.'}")
    return result


# --- Validation: too-short input bounces back to the form -------------------
guest = Client(SERVER_NAME="localhost")
resp = guest.post("/check/questions/", {"symptom_text": "short"}, follow=True)
assert resp.redirect_chain, "short input should redirect"
print("[validation] short input redirected back to form: OK")

# --- Guest flow: result shows, nothing saved --------------------------------
before = SymptomCheck.objects.count()
run_flow(guest, SYMPTOM_EN, "guest/EN")
assert SymptomCheck.objects.count() == before, "guest check must not save"
print("[guest] no DB record saved: OK")

# --- Logged-in flow: record saved --------------------------------------------
user = User.objects.create_user("smoke_p3_user", password="x9!smoke")
try:
    auth = Client(SERVER_NAME="localhost")
    auth.force_login(user)
    result = run_flow(auth, SYMPTOM_BN, "auth/BN")
    record = SymptomCheck.objects.filter(user=user).first()
    assert record is not None, "logged-in check must save a record"
    assert record.language == "Bangla", f"language stored as {record.language}"
    assert record.triage_tier == result["triage_tier"]
    print(f"[auth] record saved: language={record.language}, tier={record.triage_tier}: OK")
finally:
    SymptomCheck.objects.filter(user=user).delete()
    user.delete()

teardown_test_environment()
print("ALL P3 SMOKE TESTS PASSED")
