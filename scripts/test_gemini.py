"""Standalone Gemini connectivity test.

Sends a fixed symptom-triage prompt to the Gemini API and prints the raw
response text. Deliberately isolated: it does not import from services/ or
touch the Django app, so it can be used to verify the API key and model in
isolation before the real integration is built.

Run:  python scripts/test_gemini.py
"""
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

PROMPT = (
    "I have a headache and fever since yesterday. Generate 4 follow-up "
    "questions as a JSON array with keys: question, type. Types can be: "
    "yesno, text, number. Return JSON only, no markdown."
)


def main():
    """Load the API key, query gemini-2.0-flash, and print the raw response."""
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set in .env")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(PROMPT)
    print(response.text)


if __name__ == "__main__":
    main()
