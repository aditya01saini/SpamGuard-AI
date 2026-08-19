# SpamGuard AI

### Intelligent Email Spam, Phishing & Threat Analyzer

A production-style, full-stack AI/ML cybersecurity platform that analyzes emails
and produces a complete security report: **SAFE / SPAM / POSSIBLE PHISHING**, a
confidence score, an explainable risk score (0–100), threat indicators, URL
analysis, email statistics, an AI-generated explanation, and a recommended action.

The classification is performed by a **real trained machine-learning model** —
not hardcoded rules. A **hybrid AI architecture** combines scikit-learn ML,
rule-based phishing detection, URL heuristics, and the **Mistral API** as an
intelligent explanation layer.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [AI / ML pipeline](#ai--ml-pipeline)
4. [Why both ML and Mistral?](#why-both-ml-and-mistral)
5. [Tech stack](#tech-stack)
6. [Project structure](#project-structure)
7. [Dataset](#dataset)
8. [Model training](#model-training)
9. [Evaluation](#evaluation)
10. [Environment variables](#environment-variables)
11. [Installation](#installation)
12. [MongoDB setup](#mongodb-setup)
13. [Mistral API setup](#mistral-api-setup)
14. [API documentation](#api-documentation)
15. [Example API response](#example-api-response)
16. [Security considerations](#security-considerations)
17. [Testing](#testing)
18. [Future improvements](#future-improvements)

---

## Features

- ✅ **Real ML classification** — Multinomial Naive Bayes, Logistic Regression,
  Linear SVM, and Random Forest are trained and compared; the best is deployed.
- ✅ **NLP preprocessing pipeline** — HTML removal, lowercasing, URL/email
  stripping, number normalization, tokenization, stop-word removal, TF-IDF.
- ✅ **Phishing detection layer** — 15+ rule-based indicators (urgency, account
  suspension, credential requests, fake verification, prize scams, social
  engineering, sender patterns…).
- ✅ **URL analyzer** — extracts URLs and flags IP-address hosts, shorteners,
  encoded characters, `@` tricks, risky TLDs, suspicious domains.
- ✅ **Mistral AI** — summary, explanation, threat analysis, recommendation
  (with graceful degradation when the API is unavailable).
- ✅ **Explainable risk scoring** — transparent 0–100 score with a per-component
  breakdown (LOW / MEDIUM / HIGH / CRITICAL).
- ✅ **Email upload** — `.txt` and `.eml` (safe parsing, no attachment execution).
- ✅ **MongoDB** persistence for scan history + analytics.
- ✅ **PDF security report** download.
- ✅ **Professional dark cybersecurity dashboard** (React + Tailwind + Recharts).
- ✅ **REST API** with Pydantic validation and consistent response envelopes.
- ✅ **Security** — CORS, rate limiting, file validation, prompt-injection
  protection, secrets only in `.env`, no stack traces to clients.

---

## Architecture

```
                          ┌──────────────────────────────┐
   Paste email / upload   │         FastAPI  (REST)       │
   .txt / .eml  ────────▶ │                              │
                          │  routes → controllers →       │
                          │  services                     │
                          └──────┬───────────┬───────────┘
                                 │           │
              ┌──────────────────▼──┐   ┌────▼───────────────────┐
              │   ML pipeline        │   │  Rule-based layers      │
              │  (scikit-learn)      │   │  • phishing indicators  │
              │  TF-IDF → classifier │   │  • URL analyzer         │
              └──────────────────┬───┘   │  • keyword detector     │
                                 │       │  • risk scoring         │
                                 │       └────────────────────────┘
              ┌──────────────────▼───────────────┐
              │  Mistral AI (explanation layer)   │  ← optional, degrades gracefully
              └──────────────────┬───────────────┘
                                 │
              ┌──────────────────▼───────────────┐
              │  MongoDB  (scan history)          │  ← falls back to in-memory
              └──────────────────────────────────┘
                                 │
                          ┌──────▼───────┐
                          │ React SPA    │  dashboard / analyzer / result /
                          │ (Tailwind,   │  history / analytics / model
                          │  Recharts)   │  performance
                          └──────────────┘
```

---

## AI / ML pipeline

```
 Email
   │
   ▼
 Text preprocessing ── lowercasing, HTML removal, URL/email stripping,
 │                     number normalization, tokenization, stop-word removal
 ▼
 TF-IDF vectorization (shared vectorizer, fitted on training data only)
 │
 ▼
 ML classifier ── SAFE / SPAM (+ calibrated spam probability)
 │
 ▼
 Rule-based phishing analysis ── structured threat indicators
 │
 ▼
 URL analysis ── protocol, domain, IP-address, shortener, obfuscation checks
 │
 ▼
 Suspicious keyword detection ── supporting indicators only
 │
 ▼
 Risk scoring ── transparent 0-100 score with per-component breakdown
 │
 ▼
 Mistral API ── summary, explanation, threat analysis, recommendation
 │
 ▼
 Final security report  ── stored in MongoDB, rendered by the React app
```

---

## Why both ML and Mistral?

- **The ML model is the primary classifier.** It provides a deterministic,
  reproducible, *measurable* decision (accuracy / precision / recall / F1 on a
  held-out test set). It is fast, free, and does not depend on external services.
- **Mistral is the reasoning/explanation layer.** An LLM cannot be trusted as the
  sole classifier (hallucination risk, non-determinism, cost, latency), but it
  excels at *explaining* a decision in plain English, summarizing an email, and
  drafting a practical recommendation.

The two are kept **strictly separated** in the UI and API: the ML classification,
the rule-based indicators, and the Mistral explanation are distinct fields. If
Mistral fails or no API key is configured, the ML result and indicators are still
returned — the system degrades gracefully instead of breaking.

---

## Tech stack

| Layer        | Technology |
|--------------|-----------|
| Frontend     | React 18, Vite, Tailwind CSS, React Router, Recharts, Lucide React, Axios |
| Backend      | FastAPI, Uvicorn, Pydantic, python-multipart |
| ML / NLP     | scikit-learn, pandas, NumPy, NLTK, joblib |
| AI           | Mistral API (chat completions) |
| Database     | MongoDB (PyMongo) |
| PDF          | ReportLab |
| Testing      | pytest, pytest-asyncio, FastAPI TestClient |

---

## Project structure

```
SpamGuard-AI/
├── client/                       # React frontend
│   ├── src/
│   │   ├── components/           # Sidebar, TopNav, badges, gauge, cards…
│   │   ├── pages/                # Dashboard, Analyzer, Result, History,
│   │   │                         #   Analytics, ModelPerformance
│   │   ├── services/             # axios client, sample emails
│   │   ├── hooks/                # useApi
│   │   ├── utils/                # formatting, risk/color maps
│   │   └── App.jsx
│   ├── vite.config.js            # dev proxy /api → localhost:8000
│   ├── tailwind.config.js
│   └── .env.example
│
├── server/                       # FastAPI backend
│   ├── app/
│   │   ├── main.py               # app entry, CORS, error handlers, SPA serving
│   │   ├── config.py             # pydantic-settings (.env)
│   │   ├── routes/               # analyze, history, meta (analytics/model/health)
│   │   ├── controllers/          # orchestration (analysis pipeline)
│   │   ├── services/             # ML, phishing, url, risk, stats, keywords,
│   │   │                         #   email_parser, ai, storage, pdf
│   │   ├── schemas/              # Pydantic request/response models
│   │   ├── ai/                   # Mistral client + prompt safety
│   │   ├── security/             # rate limiter
│   │   └── utils/                # exceptions, response envelope, logging
│   ├── ml/                       # standalone ML package
│   │   ├── train_model.py        # training + evaluation + artifact saving
│   │   ├── preprocess.py         # shared NLP preprocessing
│   │   ├── predict.py            # model loading + inference
│   │   └── saved_models/         # model.joblib, vectorizer.joblib, metrics.json
│   ├── tests/                    # ML, API, and security tests
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
│
├── data/                         # dataset (gitignored, auto-downloadable)
├── README.md
└── .gitignore
```

---

## Dataset

The training pipeline uses the **Enron-Spam** public corpus
(Metsis, Androutsopoulos & Paliouras, 2006), consolidated into a single CSV
(~33,700 real emails — 17,171 spam / 16,545 ham).

`train_model.py` will automatically download and extract the dataset if
`data/enron_spam_data.csv` is not present.

---

## Model training

```bash
cd server
python3 -m pip install -r requirements.txt
python3 -m nltk.downloader stopwords punkt

# Train all four models, evaluate, and save the best
python3 ml/train_model.py
```

The script loads the dataset, cleans it, combines subject + body, preprocesses
the text, splits train/test (80/20, stratified), fits a shared TF-IDF vectorizer,
trains and evaluates four classifiers, selects the best by F1 score, and saves:

- `saved_models/model.joblib` — the winning model
- `saved_models/vectorizer.joblib` — the TF-IDF vectorizer
- `saved_models/preprocess_config.json` — preprocessing/vectorizer configuration
- `saved_models/metrics.json` — full evaluation metrics for all models

---

## Evaluation

Measured on a held-out test set of ~6,100 emails:

| Model                    | Accuracy | Precision | Recall | F1     |
|--------------------------|----------|-----------|--------|--------|
| **Linear SVM** ✅        | 99.13%   | 98.94%    | 99.25% | 99.09% |
| Logistic Regression      | 98.92%   | 98.24%    | 99.52% | 98.88% |
| Multinomial Naive Bayes  | 98.49%   | 98.36%    | 98.49% | 98.42% |
| Random Forest            | 98.28%   | 97.63%    | 98.80% | 98.21% |

**Linear SVM** is selected as the production model. Full per-model confusion
matrices are available on the **Model Performance** page and via
`GET /api/model-info`.

---

## Environment variables

### Backend (`server/.env`)

Copy `server/.env.example` to `server/.env`:

```
MISTRAL_API_KEY=your_mistral_api_key_here   # optional — AI layer degrades gracefully
MISTRAL_MODEL=mistral-small-latest
MONGODB_URI=mongodb://localhost:27017/spamguard
PORT=8000
CLIENT_URL=http://localhost:5173
MAX_FILE_SIZE_MB=5
```

### Frontend (`client/.env`)

```
VITE_API_BASE_URL=/api   # never put backend secrets here
```

> ⚠️ The Mistral API key lives **only** in the backend `.env`. It is never sent
> to the browser and must never appear in frontend code.

---

## Installation

### 1. Backend

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m nltk.downloader stopwords punkt
cp .env.example .env          # then fill in your values
python3 ml/train_model.py     # train + save the model (one time)
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (development)

```bash
cd client
npm install
npm run dev                   # http://localhost:5173 (proxies /api → :8000)
```

### 3. Frontend (production — served by FastAPI)

```bash
cd client && npm run build    # outputs client/dist
# FastAPI automatically serves client/dist when present
cd ../server && uvicorn app.main:app --port 8000
# open http://localhost:8000
```

---

## MongoDB setup

Install and run MongoDB (any local instance works):

```bash
# e.g. with Docker
docker run -d -p 27017:27017 --name spamguard-mongo mongo:7

# or a local install
mongod --dbpath /path/to/data
```

The backend connects using `MONGODB_URI`. **If MongoDB is unreachable, the app
falls back to an in-memory store** and logs a warning — everything keeps working.

---

## Mistral API setup

1. Create an account at [console.mistral.ai](https://console.mistral.ai).
2. Generate an API key.
3. Add it to `server/.env` as `MISTRAL_API_KEY=…`.
4. (Optional) set `MISTRAL_MODEL` (default `mistral-small-latest`).

If the key is missing or invalid, the ML classification and rule-based analysis
are still returned with a note that the AI explanation is temporarily unavailable.

---

## API documentation

Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

| Method | Endpoint                  | Description |
|--------|---------------------------|-------------|
| POST   | `/api/analyze`            | Analyze a pasted email (`{subject, sender, body}`) |
| POST   | `/api/analyze/upload`     | Analyze an uploaded `.txt` / `.eml` file (multipart) |
| GET    | `/api/history`            | Scan history (`?limit&skip&classification&search`) |
| GET    | `/api/history/{id}`       | Get a specific scan |
| DELETE | `/api/history/{id}`       | Delete a scan |
| GET    | `/api/history/{id}/report`| Download PDF security report |
| GET    | `/api/analytics`          | Dashboard analytics |
| GET    | `/api/model-info`         | Model name + evaluation metrics |
| GET    | `/api/health`             | Health check |

---

## Example API response

```json
{
  "success": true,
  "data": {
    "classification": "POSSIBLE PHISHING",
    "classification_reason": "ML classified the email as spam and phishing indicators are present.",
    "confidence": 0.9996,
    "spam_probability": 0.9996,
    "safe_probability": 0.0004,
    "phishing_probability": 0.95,
    "risk_score": 96,
    "risk_level": "CRITICAL",
    "risk_breakdown": [
      { "component": "ML spam probability", "points": 49.98, "detail": "..." },
      { "component": "Phishing indicators", "points": 25.0, "detail": "..." },
      { "component": "Suspicious URLs", "points": 15.0, "detail": "..." },
      { "component": "Suspicious keywords", "points": 7.8, "detail": "..." }
    ],
    "suspicious_keywords": ["suspended", "urgent", "verify", "password"],
    "threat_indicators": [
      {
        "indicator": "Account suspension threat",
        "severity": "HIGH",
        "category": "phishing",
        "description": "Threatens that an account will be suspended, locked or terminated."
      }
    ],
    "urls": [
      { "url": "http://83.102.44.9/verify", "domain": "83.102.44.9",
        "protocol": "http", "is_https": false, "severity": "HIGH",
        "risk_indicators": [{ "indicator": "IP-address URL", "severity": "HIGH", "description": "…" }] }
    ],
    "statistics": { "word_count": 48, "url_count": 1, "has_html": false, "…": "…" },
    "ai_analysis": {
      "available": true, "provider": "mistral",
      "summary": "…", "explanation": "…", "threat_analysis": "…"
    },
    "recommendation": "Do not click any links or provide personal information…",
    "model_name": "Linear SVM"
  }
}
```

---

## Security considerations

- **Secrets** are loaded from `.env` only; `.env` is gitignored, `.env.example`
  holds safe placeholders. No API keys or credentials in source code or frontend.
- **Prompt-injection protection** — email content is wrapped in a controlled
  prompt that instructs Mistral to treat it as *untrusted data* and ignore any
  instructions inside it.
- **Untrusted email handling** — uploaded `.eml` files are parsed with the
  standard-library email parser; attachments are counted but never executed or
  opened; embedded scripts are not run.
- **Input validation** — Pydantic schemas, file extension/MIME checks, and a
  configurable size limit (`MAX_FILE_SIZE_MB`).
- **Secure errors** — global exception handlers return sanitized messages; stack
  traces and secrets are never exposed to clients.
- **CORS** restricted to the configured client origin.
- **Rate limiting** — a lightweight in-memory sliding-window limiter on analysis.
- **Cautious language** — URLs/indicators are described as *suspicious* /
  *potentially unsafe* / *possible phishing* rather than asserted malicious.

---

## Testing

```bash
cd server
python3 -m pytest tests/ -v
```

Tests cover:

- **ML** — preprocessing (lowercase/HTML/stop-words), model loading, prediction.
- **API** — health, analyze, upload, history CRUD, model-info, analytics, PDF.
- **Security** — invalid extension, empty file, oversized file, malformed `.eml`,
  prompt-injection attempts.

Mistral is **mocked** in tests — no real API calls are made.

---

## Future improvements

- Persist TF-IDF vocabulary metadata + model card for reproducibility.
- Docker Compose for one-command local startup (Mongo + backend + frontend).
- External URL reputation lookups (VirusTotal / Google Safe Browsing) as an
  optional configured provider.
- User accounts / authentication and per-user scan history.
- Scheduled model retraining and drift monitoring.
- Streaming LLM responses for faster perceived latency.
```
