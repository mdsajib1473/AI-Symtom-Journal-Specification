"""Views for the symptom checker — a three-step flow.

Step 1 renders the symptom form, step 2 returns AI follow-up questions, and
step 3 returns the triage result. All AI work is delegated to
services.ai_service; these views only validate input and manage session state.
"""
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from services.ai_service import (
    detect_language,
    get_follow_up_questions,
    get_triage_result,
)

from .models import SymptomCheck

# Session keys for in-progress checks (cleared once the result is shown).
SESSION_SYMPTOM = "checker_symptom_text"
SESSION_QUESTIONS = "checker_questions"
SESSION_LANGUAGE = "checker_language"

MIN_SYMPTOM_LENGTH = 10
MAX_SYMPTOM_LENGTH = 1000


def symptom_form_view(request):
    """Step 1 — render the symptom description form (guests welcome)."""
    return render(request, "checker/symptom_form.html")


@require_POST
def get_questions_view(request):
    """Step 2 — validate the symptom text and show AI follow-up questions."""
    symptom_text = request.POST.get("symptom_text", "").strip()

    if not MIN_SYMPTOM_LENGTH <= len(symptom_text) <= MAX_SYMPTOM_LENGTH:
        messages.error(
            request,
            f"Please describe your symptoms in {MIN_SYMPTOM_LENGTH} to "
            f"{MAX_SYMPTOM_LENGTH} characters.",
        )
        return redirect("checker:symptom_form")

    language = detect_language(symptom_text)
    questions = get_follow_up_questions(symptom_text, language)

    request.session[SESSION_SYMPTOM] = symptom_text
    request.session[SESSION_QUESTIONS] = questions
    request.session[SESSION_LANGUAGE] = language

    return render(
        request,
        "checker/follow_up.html",
        {"symptom_text": symptom_text, "questions": questions},
    )


@require_POST
def get_result_view(request):
    """Step 3 — collect answers, get the triage result, and show the card.

    Logged-in users get a SymptomCheck record saved; guests just see the
    result. The in-progress session data is cleared either way.
    """
    symptom_text = request.session.get(SESSION_SYMPTOM)
    questions = request.session.get(SESSION_QUESTIONS)
    language = request.session.get(SESSION_LANGUAGE)

    if not (symptom_text and questions and language):
        messages.error(request, "Your session expired. Please start again.")
        return redirect("checker:symptom_form")

    questions_and_answers = [
        {
            "question": q["question"],
            "answer": request.POST.get(f"answer_{i}", "").strip(),
        }
        for i, q in enumerate(questions, start=1)
    ]

    result = get_triage_result(symptom_text, questions_and_answers, language)

    if request.user.is_authenticated:
        SymptomCheck.objects.create(
            user=request.user,
            symptom_description=symptom_text,
            follow_up_questions=questions,
            follow_up_answers={
                qa["question"]: qa["answer"] for qa in questions_and_answers
            },
            ai_result=result,
            language=language,
            triage_tier=result["triage_tier"],
        )

    for key in (SESSION_SYMPTOM, SESSION_QUESTIONS, SESSION_LANGUAGE):
        request.session.pop(key, None)

    return render(
        request, "checker/result.html", {"result": result, "language": language}
    )
