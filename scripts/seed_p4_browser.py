"""Seed a browser-test user with two history entries (EN green, BN red).

Run:  python manage.py shell -c "exec(open('scripts/seed_p4_browser.py', encoding='utf-8').read())"
"""
from django.contrib.auth.models import User

from apps.checker.models import SymptomCheck

DISCLAIMER = "This is not a medical diagnosis. Consult a qualified doctor."

user, _ = User.objects.get_or_create(username="p4_browser")
user.set_password("browser-test-9x!")
user.save()

SymptomCheck.objects.filter(user=user).delete()

SymptomCheck.objects.create(
    user=user,
    symptom_description="Headache and mild fever since yesterday morning, worse at night.",
    follow_up_questions=[{"question": "How long?", "type": "number"}],
    follow_up_answers={"How long?": "2"},
    ai_result={
        "possible_conditions": [{"name": "Tension headache", "description": "Often stress-related."}],
        "triage_tier": "green",
        "recommended_action": "Rest and hydrate.",
        "warning_signs": ["Pain becomes severe"],
        "disclaimer": DISCLAIMER,
    },
    language="English",
    triage_tier="green",
)

SymptomCheck.objects.create(
    user=user,
    symptom_description="গতকাল থেকে মাথা ব্যথা এবং জ্বর",
    follow_up_questions=[{"question": "কত দিন?", "type": "number"}],
    follow_up_answers={"কত দিন?": "2"},
    ai_result={
        "possible_conditions": [{"name": "মাইগ্রেন", "description": "তীব্র মাথা ব্যথা।"}],
        "triage_tier": "red",
        "recommended_action": "দ্রুত হাসপাতালে যান।",
        "warning_signs": ["জ্ঞান হারানো"],
        "disclaimer": DISCLAIMER,
    },
    language="Bangla",
    triage_tier="red",
)

print("seeded:", SymptomCheck.objects.filter(user=user).count(), "checks")
