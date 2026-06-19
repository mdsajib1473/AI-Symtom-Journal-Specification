# SymptomAI - AI Symptom Triage Journal

[![Live Demo](https://img.shields.io/badge/Live%20Demo-symptom--ai--journal.onrender.com-0F766E?style=for-the-badge)](https://symptom-ai-journal.onrender.com)

## Project Overview

SymptomAI is a Django-based web application that helps users understand their symptoms through an AI-powered triage workflow. Users describe how they feel in Bangla or English, and the AI asks targeted follow-up questions before returning a triage assessment with possible conditions, a recommended action tier (green / yellow / red), and important warning signs. The platform supports both guest and registered users, with registered users able to save and review their full symptom history. This is a portfolio project demonstrating full-stack Django development with AI integration, multilingual support, and production deployment on Render.com.

## Why This Project?

AI Symptom Journal is the only AI symptom checker that speaks Bangla natively, asks personalized follow-up questions using an LLM, and delivers a full triage result to any guest - no account, no app download, no English required.

## Live Website

## https://symptom-ai-journal.onrender.com/

## Features

### User-Facing Features

Any visitor can complete a full symptom check without creating an account. Users describe their symptoms in a free-text field (Bangla or English), and the AI generates exactly four targeted follow-up questions - rendered as Yes/No pill toggles, text inputs, or number inputs depending on the question type. After answering, a triage result card displays possible conditions, a colour-coded action tier (green = rest at home, yellow = see a doctor soon, red = seek urgent care), specific warning signs to watch for, and a medical disclaimer. Registered users can log in to have each check saved automatically to a personal history timeline, where they can expand any past result to review the full detail or soft-delete entries they no longer need. The entire interface is mobile-responsive and works in both Bangla and English - language detection is automatic based on the script of the user's input.

### AI Integration

The AI layer is powered by the Groq API (model: `llama-3.3-70b-versatile`) called via a standard OpenAI-compatible REST interface. All API communication is isolated in `services/ai_service.py` - views never talk to the API directly. The service includes robust fallback logic: if the API is unreachable or returns unparseable output, the user receives a safe set of generic follow-up questions or a yellow-tier "consult a doctor" result rather than an error page. The Bangla disclaimer is enforced in code and cannot be omitted by the AI.

### Security and Data Handling

All forms use Django's built-in CSRF protection. User inputs are validated server-side (10–1000 character range for symptom descriptions). Ownership is enforced on delete operations - users can only soft-delete their own records, with a 403 returned on any attempt to access another user's data. History entries are soft-deleted (`is_deleted=True`) rather than permanently removed. Session data for in-progress checks is cleared immediately after the result is displayed.

## Screenshots

![Homepage](screenshots/Homepage.png)
![Check page](screenshots/check.png)
![Follow Up Questions](screenshots/questions.png)
![AI Results](screenshots/results.png)
![Check page](screenshots/check2.png)
![Follow Up Questions](screenshots2/questions2.png)
![AI Results](screenshots/results2.png)


## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 5.2 |
| **Database** | PostgreSQL (hosted on Supabase) |
| **AI Provider** | Groq API - model `llama-3.3-70b-versatile` |
| **Auth** | Django built-in authentication |
| **Frontend Styling** | Tailwind CSS via CDN (brand teal `#0F766E`, mobile-responsive) |
| **JavaScript** | Vanilla JS only - no React, Vue, or jQuery |
| **Static Files** | WhiteNoise (compressed manifest storage in production) |
| **Deployment** | Render.com (free tier, automatic HTTPS) |
| **WSGI Server** | Gunicorn |
| **Environment Variables** | python-dotenv |

## Project Structure

```
├── symptom_journal/        # Django project configuration (settings, root URLs, WSGI)
├── apps/
│   ├── checker/            # Symptom check feature (form, follow-up questions, triage result)
│   ├── accounts/           # User registration and login
│   └── history/            # History timeline and soft delete
├── services/
│   └── ai_service.py       # ALL Groq API calls (language detection, follow-up questions, triage result)
├── templates/              # HTML templates (base layout, checker flow, history, auth)
├── static/                 # Static files (CSS, images)
├── scripts/                # Utility scripts (connectivity test, smoke tests, seed data)
├── build.sh                # Render deployment script (install, collectstatic, migrate)
├── Procfile                # Gunicorn start command
├── runtime.txt             # Python version pin
└── .env.example            # Environment variable template
```

## Local Development Setup

### Prerequisites

- Python 3.12 or higher
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/mdsajib1473/AI-Symtom-Journal-Specification.git
cd AI-Symtom-Journal-Specification
```

### Step 2: Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root. See `.env.example` for all available keys:

```env
SECRET_KEY=your-long-random-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME

# Groq AI
GROQ_API_KEY=your-groq-api-key-here

# Production only (leave blank for local dev)
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=
```

Get a free Groq API key at [console.groq.com](https://console.groq.com/keys).

Generate a secure `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to use the app.

## Deployment on Render

1. Push the repository to GitHub.
2. Create a new **Web Service** on Render, connected to your GitHub repo.
3. Set the following in the Render dashboard:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn symptom_journal.wsgi:application`
4. Add the following environment variables:
   - `SECRET_KEY` - generate a fresh 50+ character key
   - `DEBUG` - `False`
   - `DATABASE_URL` - your Supabase PostgreSQL connection string
   - `GROQ_API_KEY` - your Groq API key
   - `ALLOWED_HOSTS` - `your-app-name.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` - `https://your-app-name.onrender.com`

Render will run `build.sh` on each deploy, which installs dependencies, collects static files, and applies any pending migrations automatically.

## Verify the AI Connection

Run the standalone connectivity test (no Django required):

```bash
python scripts/test_ai.py
```

A successful response prints a JSON array of four follow-up questions. If you see a `401`, check your `GROQ_API_KEY`. If you see a `429`, you have hit the free-tier rate limit - wait a moment and retry.

## Disclaimer

SymptomAI is not a medical device and does not provide medical diagnoses. Every triage result includes the disclaimer: *"This is not a medical diagnosis. Consult a qualified doctor."* This application is intended for portfolio and educational purposes only.
