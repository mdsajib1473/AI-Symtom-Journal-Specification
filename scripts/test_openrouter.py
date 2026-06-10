"""Standalone OpenRouter connectivity test.

Sends a fixed symptom-triage prompt to the OpenRouter API (Llama 3.3 70B free tier)
and prints the raw response text. Deliberately isolated: no Django imports, no
services/ dependencies — purely verifies the key and model before P3 integration.

Run:  python scripts/test_openrouter.py
"""
import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPT = (
    "I have a headache and fever since yesterday. Generate 4 follow-up "
    "questions as a JSON array with keys: question, type. Types can be: "
    "yesno, text, number. Return JSON only, no markdown."
)


def main():
    """Load the API key, query Llama 3.3 70B via OpenRouter, and print the response."""
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        "messages": [{"role": "user", "content": PROMPT}],
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    if not response.ok:
        print(f"HTTP {response.status_code}: {response.text}")
        response.raise_for_status()

    data = response.json()
    text = data["choices"][0]["message"]["content"]
    print(text)


if __name__ == "__main__":
    main()
