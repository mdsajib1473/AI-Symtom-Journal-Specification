# Competitive Analysis: AI Symptom Journal

**Project:** AI Symptom Journal - Triage Assistant
**Author:** Sajib (portfolio project)
**Date:** June 2026

---

## 1. Competitor Overview

The following six tools represent the most widely used symptom checkers available globally. Each was evaluated across eight dimensions relevant to the positioning of AI Symptom Journal.

---

## 2. Comparison Table

| Dimension | Ada Health | WebMD Symptom Checker | Healthline | Mayo Clinic | Symptomate | Healthily (Your.MD) | **AI Symptom Journal** |
|---|---|---|---|---|---|---|---|
| **AI Approach** | Probabilistic ML + knowledge base | Hybrid rule-based + AI diagnostic engine | Editorial/curated content only (no real checker) | Rule-based selection engine | Probabilistic ML (Infermedica engine) | AI-powered chat + medical knowledge base | LLM (Groq `llama-3.3-70b-versatile`) |
| **Conversation Style** | Chat (conversational, NLP in US only) | Form + body map + checkbox | Article links (no checker) | Form + dropdown selection | Form + adaptive checkbox questions | Chat (chatbot named DOT) | Chat + dynamic typed follow-ups |
| **Bangla Support** | No (English, German, French, Portuguese, Spanish) | No (English and Spanish only) | No (English only) | No (English only) | No (15 languages, none South Asian) | No (English primary) | **Yes - native Bangla input and responses** |
| **Triage Output** | Possible conditions + care pathway | List of conditions + article links | No triage output | Possible conditions + article links | Conditions + urgency tier + next steps | Conditions + self-care guidance + what to do | Conditions + green/yellow/red tier + warning signs + disclaimer |
| **Account Required** | Yes (required to save or view full results) | No | N/A | No (public); Yes (patient portal) | No (anonymous) | Optional (full features need account) | Optional (guest checks work; login unlocks history) |
| **Mobile App** | Yes (iOS + Android) | Yes (iOS + Android) | No | No | Yes (iOS + Android) | Yes (iOS + Android) | No (mobile-responsive web) |
| **Free to Use** | Yes (free for individuals) | Yes | Yes | Yes | Yes (freemium for enterprise) | Yes (basic free) | Yes (completely free) |
| **Key Weakness** | Account wall before results; NLP input US-only only; no South Asian language support | Rigid checkbox/body-map UI; no conversational follow-up; English and Spanish only | Not a real symptom checker - redirects to articles | Extremely rigid dropdown selection; no AI reasoning; English only | Multiple-choice only; no free-text or LLM reasoning; no Bangla or South Asian languages | English-focused; account encouraged for full use; no Bangla | No native mobile app; no doctor network; portfolio scope only |

---

## 3. Positioning: Where Does AI Symptom Journal Fit?

### The gap none of the competitors address

Every major symptom checker in the comparison table serves Western or global English-speaking audiences as a primary market. None of them support Bangla. Bangladesh has approximately 170 million people, making it the eighth most populous country in the world, with Bangla as the native language for over 230 million speakers globally. Yet not a single established symptom checker - not Ada, not Symptomate with its 15 languages, not Healthily - has shipped Bangla support. This is not a minor omission. A user who can only read Bangla cannot meaningfully use any of the tools above. AI Symptom Journal is built from the ground up to handle both Bangla and English input natively, with automatic language detection based on Unicode script analysis, and the AI responds in whichever language the user typed. For a Bangladeshi user, this is the first tool in this category that actually works for them.

### Why Bangla support is a meaningful differentiator in the Bangladeshi market

Bangladesh's digital health market is growing rapidly. Government-backed initiatives under "Digital Bangladesh" have accelerated mobile health adoption, and telemedicine apps like Doctorola, Praava, and Seba.xyz now serve millions of users - but none offer AI-powered symptom triage in Bangla. The closest existing tools are appointment-booking apps, not triage assistants. AI Symptom Journal occupies an entirely empty space: LLM-powered conversational triage in the user's native language, accessible without installation, from any browser on any device. For a user in Dhaka or Sylhet who describes chest tightness in Bangla, this tool responds in Bangla - including the follow-up questions, the triage result, and the medical disclaimer. No competitor does this.

### Why LLM-powered follow-up questions are a technical differentiator

The majority of competitors - WebMD, Mayo Clinic, and Symptomate - rely on rigid checkbox interfaces or fixed dropdown menus. The user selects from a predefined symptom list; the system applies rule-based logic to generate a result. The follow-up questions do not change based on what the user said. Ada Health and Healthily are closer to conversational, but their AI layers are proprietary ML systems trained on structured medical data. AI Symptom Journal takes a different approach: it sends the user's free-text symptom description to a large language model (Groq's `llama-3.3-70b-versatile`), which generates four targeted follow-up questions specific to what the user described. If a user types "I have had a sharp pain behind my right eye for two days," the follow-up questions are about that specific complaint - not a generic set. The question types adapt too: yes/no toggles, short text inputs, and numeric inputs for duration or severity. This produces a more clinically relevant result than any checkbox-based competitor can achieve.

### How optional login lowers the barrier to entry

Ada Health requires account creation before a user can complete a full symptom check. Healthily strongly encourages registration to unlock full results. Creating an account - entering an email, verifying it, setting a password - is a meaningful friction point, especially for a first-time user who just wants to know whether their headache warrants a doctor visit. AI Symptom Journal follows a guest-first model: any visitor can complete a full three-step symptom check, receive a triage result with colour-coded urgency, and see their possible conditions - all without creating an account or giving up any personal information. Registration is offered as an optional upgrade that unlocks a personal history timeline, not as a gate to the core feature. This directly addresses one of the most common drop-off points in the competitor tools.

---

## 4. Unique Value Proposition

Three variations, ordered from most specific to most concise:

**Variation 1 (most specific - best for technical audiences):**
"AI Symptom Journal is the only LLM-powered symptom triage tool that accepts free-text input in Bangla or English, generates context-aware follow-up questions, and returns a colour-coded urgency result - with no account required - for Bangladeshi users who have no equivalent tool in their native language."

**Variation 2 (balanced - best for README or scholarship application):**
"AI Symptom Journal is the only AI symptom checker that speaks Bangla natively, asks personalized follow-up questions using an LLM, and delivers a full triage result to any guest - no account, no app download, no English required."

**Variation 3 (most concise - best for one-liners):**
"AI Symptom Journal is the only conversational triage assistant that lets Bangla speakers describe their symptoms in their own words and get an AI-powered urgency assessment - instantly, anonymously, and for free."

---

## 5. Portfolio Talking Points

The following five points are written for Sajib to use when presenting this project to a university admission board, scholarship committee, or professor evaluating technical merit. Each references a concrete technical decision made in the project.

- **LLM integration with production-hardened fallback logic:** The `services/ai_service.py` module wraps every Groq API call in structured exception handling that returns a safe, language-appropriate fallback result on any network or parsing failure - meaning the app never shows an error page to a user, a deliberate defensive design decision that mirrors production engineering practice.

- **Automatic Bangla language detection using Unicode script analysis:** Language detection is implemented without any third-party library by measuring the proportion of Bengali Unicode characters (U+0980 to U+09FF) in the user's input, with a 30% threshold triggering Bangla mode - a lightweight, dependency-free solution to a real multilingual UX problem affecting 230 million speakers.

- **Stateless guest session architecture:** The three-step symptom check flow (form, follow-up questions, result) is managed entirely through Django's signed session framework, storing in-progress check data server-side and purging it immediately after the result is shown, which eliminates the need for a user account while keeping data off the client.

- **Full-stack Django deployment on free infrastructure:** The project is deployed on Render.com using a custom `build.sh` script that chains dependency installation, WhiteNoise static file compression, and PostgreSQL migrations into a single automated hook, with Supabase providing a production PostgreSQL database at zero cost - demonstrating practical knowledge of production deployment constraints.

- **Security-first data model with soft delete:** History entries are never permanently deleted; instead, an `is_deleted` boolean flag is toggled, and ownership is enforced at the view layer with a hard 403 response on any cross-user access attempt - design choices that reflect awareness of both data safety and access control beyond what introductory courses typically cover.

---

*This document was prepared as part of the AI Symptom Journal portfolio project. All competitor information is based on publicly available sources as of June 2026.*
