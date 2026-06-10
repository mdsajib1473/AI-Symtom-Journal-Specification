"""All OpenRouter AI calls for the symptom checker live in this module.

Views must never talk to the API directly — they call the two public helpers:

    get_follow_up_questions(symptom_text, language) -> list[dict]
    get_triage_result(symptom_text, questions_and_answers, language) -> dict

Both helpers are hardened for the request/response cycle: any network, HTTP,
or JSON-parsing failure is caught and a safe fallback is returned instead, so
an AI outage can never crash a view.
"""
import json
import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
REQUEST_TIMEOUT = 30  # seconds

# Required on every triage result, exactly as written (Agent.md rule 3).
DISCLAIMER = "This is not a medical diagnosis. Consult a qualified doctor."

VALID_TIERS = ("green", "yellow", "red")

QUESTIONS_INSTRUCTION = """You are a medical triage assistant. You do NOT diagnose.
Based on the symptom description, generate exactly 4 targeted follow-up questions
to better understand the patient's condition.
Respond ONLY in {language}.
Return ONLY a valid JSON array, no markdown, no explanation:
[
  {{"question": "...", "type": "yesno"}},
  {{"question": "...", "type": "text"}},
  {{"question": "...", "type": "number"}},
  {{"question": "...", "type": "yesno"}}
]
Question types: "yesno" (Yes/No radio), "text" (short text input), "number" (numeric input for duration/severity)."""

TRIAGE_INSTRUCTION = """You are a medical triage assistant. You do NOT diagnose.
Based on the symptom description and the follow-up answers provided,
return a triage assessment.
Respond ONLY in {language}.
Return ONLY valid JSON, no markdown, no explanation:
{{
  "possible_conditions": [
    {{"name": "...", "description": "..."}},
    {{"name": "...", "description": "..."}}
  ],
  "triage_tier": "green" or "yellow" or "red",
  "recommended_action": "...",
  "warning_signs": ["...", "...", "..."],
  "disclaimer": "This is not a medical diagnosis. Consult a qualified doctor."
}}
triage_tier values: green = rest at home, yellow = see a GP, red = seek urgent care.
Always include the disclaimer exactly as shown."""

# Served when the AI is unreachable or returns something unparseable.
FALLBACK_QUESTIONS = {
    "English": [
        {"question": "How many days have you had these symptoms?", "type": "number"},
        {"question": "Do you have a fever?", "type": "yesno"},
        {"question": "Are the symptoms getting worse?", "type": "yesno"},
        {"question": "Do you have any other symptoms you haven't mentioned?", "type": "text"},
    ],
    "Bangla": [
        {"question": "কত দিন ধরে এই উপসর্গগুলো আছে?", "type": "number"},
        {"question": "আপনার কি জ্বর আছে?", "type": "yesno"},
        {"question": "উপসর্গগুলো কি দিন দিন খারাপ হচ্ছে?", "type": "yesno"},
        {"question": "আর কোনো উপসর্গ আছে কি যা উল্লেখ করেননি?", "type": "text"},
    ],
}

FALLBACK_RESULT = {
    "English": {
        "possible_conditions": [],
        "triage_tier": "yellow",
        "recommended_action": (
            "We could not analyse your symptoms automatically right now. "
            "To be safe, please consult a general practitioner about your symptoms."
        ),
        "warning_signs": [],
        "disclaimer": DISCLAIMER,
    },
    "Bangla": {
        "possible_conditions": [],
        "triage_tier": "yellow",
        "recommended_action": (
            "এই মুহূর্তে আপনার উপসর্গ স্বয়ংক্রিয়ভাবে বিশ্লেষণ করা যায়নি। "
            "নিরাপদ থাকতে অনুগ্রহ করে একজন ডাক্তারের সাথে পরামর্শ করুন।"
        ),
        "warning_signs": [],
        "disclaimer": DISCLAIMER,
    },
}


def detect_language(text):
    """Return "Bangla" if over 30% of the text is Bengali script, else "English"."""
    if not text:
        return "English"
    bengali_chars = sum(1 for ch in text if "ঀ" <= ch <= "৿")
    return "Bangla" if bengali_chars / len(text) > 0.30 else "English"


def get_follow_up_questions(symptom_text, language):
    """Ask the AI for 4 follow-up questions about the described symptoms.

    Returns a list of {"question": str, "type": "yesno"|"text"|"number"} dicts.
    Falls back to 4 generic questions in the user's language on any failure.
    """
    try:
        raw = _chat(
            system=QUESTIONS_INSTRUCTION.format(language=language),
            user=symptom_text,
        )
        questions = _extract_json(raw)
        if _valid_questions(questions):
            return questions
        logger.warning("AI returned malformed questions, using fallback: %r", raw)
    except Exception:
        logger.exception("Follow-up question generation failed, using fallback")
    return FALLBACK_QUESTIONS[language]


def get_triage_result(symptom_text, questions_and_answers, language):
    """Ask the AI for a triage assessment given symptoms and follow-up answers.

    `questions_and_answers` is a list of {"question": str, "answer": str} dicts.
    Returns the parsed result dict; the disclaimer and a valid triage tier are
    always enforced. Falls back to a safe "yellow" result on any failure.
    """
    qa_lines = "\n".join(
        f"Q: {qa['question']}\nA: {qa['answer']}" for qa in questions_and_answers
    )
    prompt = f"Symptoms: {symptom_text}\n\nFollow-up answers:\n{qa_lines}"

    try:
        raw = _chat(
            system=TRIAGE_INSTRUCTION.format(language=language),
            user=prompt,
        )
        result = _extract_json(raw)
        if _valid_result(result):
            result["disclaimer"] = DISCLAIMER
            return result
        logger.warning("AI returned malformed triage result, using fallback: %r", raw)
    except Exception:
        logger.exception("Triage result generation failed, using fallback")
    return FALLBACK_RESULT[language]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _chat(system, user):
    """Send one system+user exchange to OpenRouter and return the reply text."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _extract_json(text):
    """Parse JSON from a model reply, tolerating ```json fences and prose."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    # Trim any prose before/after the outermost JSON value.
    start = min((i for i in (text.find("["), text.find("{")) if i != -1), default=0)
    end = max(text.rfind("]"), text.rfind("}")) + 1 or len(text)
    return json.loads(text[start:end])


def _valid_questions(questions):
    """Check the parsed reply is a list of well-formed question dicts."""
    return (
        isinstance(questions, list)
        and len(questions) > 0
        and all(
            isinstance(q, dict)
            and q.get("question")
            and q.get("type") in ("yesno", "text", "number")
            for q in questions
        )
    )


def _valid_result(result):
    """Check the parsed reply has the required triage fields."""
    return (
        isinstance(result, dict)
        and result.get("triage_tier") in VALID_TIERS
        and isinstance(result.get("possible_conditions"), list)
        and result.get("recommended_action")
        and isinstance(result.get("warning_signs"), list)
    )
