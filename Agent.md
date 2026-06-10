# Agent.md — AI Symptom Journal: Triage Assistant
# Read this file before writing any code. Follow it strictly.

## Project Purpose
A Django web app where users describe symptoms in Bangla or English.
The AI asks follow-up questions, then returns possible conditions
and a recommended action tier (green / yellow / red).
This is a portfolio project — code must be clean and well-commented.

## Tech Stack — DO NOT change any of these
- Backend: Django 5.x
- Database: PostgreSQL (psycopg2-binary)
- AI: Groq API — model: llama-3.3-70b-versatile
- Auth: Django built-in auth only (no OAuth, no allauth)
- CSS: Tailwind CSS via CDN
- JS: Vanilla JavaScript only — NO React, Vue, or jQuery
- Deployment: Render.com (free tier)
- Static files: WhiteNoise
- Env vars: python-dotenv

## App Structure
symptom_journal/     → Django project config
apps/checker/        → symptom check feature
apps/accounts/       → auth (signup, login, logout)
apps/history/        → history timeline
services/ai_service.py      → ALL AI (Groq) API calls go here only

## Build Order
P1 → Project setup + design system + home page
P2 → Auth (signup, login, logout) + base template
P3 → Symptom form + AI follow-up questions
P4 → Triage result card + save to DB
P5 → History timeline + delete + Render deploy config

## Current step: P3

## IN SCOPE
- Guest symptom check (no login required)
- Follow-up questions from Claude (3-5 questions, shown all at once)
- Triage result: possible conditions + green/yellow/red tier + disclaimer
- User registration and login (optional — unlocks history)
- History timeline for logged-in users
- Delete a history entry
- Bangla + English language support
- Mobile-responsive design
- Render.com deployment

## OUT OF SCOPE — do not build these under any circumstances
- Doctor booking or telemedicine
- Medication or drug name recommendations
- Mental health / psychiatric triage
- Push notifications or email alerts
- Admin dashboard or analytics
- Social sharing of results
- PDF export
- Payment or subscription
- Google/Facebook OAuth login
- Real-time chat or websockets
- Mobile native app

## Rules
1. Never build beyond the current step
2. Always respond in the same language the user typed (Bangla → Bangla)
3. Every triage result MUST include the disclaimer:
   "This is not a medical diagnosis. Consult a qualified doctor."
4. Commit and push code if/when necessary with 3 to 5 words.
5. Write clean, well-commented code — every function and class must have a docstring.
6. Follow secure coding practices — never expose secrets, always use CSRF protection,
   validate and sanitize all user inputs before processing.
7. Write scalable code — keep business logic in services/, keep views thin,
   never hardcode values that belong in settings or .env.
8. Do not over-comment — only comment where the code is not self-explanatory.
   Avoid stating the obvious (e.g. # increment counter above i += 1).
