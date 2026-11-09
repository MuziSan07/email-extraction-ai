# Email Business Info Extractor

A FastAPI application that extracts structured business contact information
(name, title, company, email, phone, address, website) from email text using an
LLM (Groq via LangChain). Results are stored in SQLite and viewable in an admin
panel. An optional Gmail integration can pull recent inbox messages and extract
from them directly.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Features

- **AI extraction** of business contact fields from free-form email text.
- **Web UI** to paste an email and view structured results.
- **JSON API** (`POST /api/extract`) for programmatic use.
- **Admin panel** to browse and delete stored contacts.
- **Optional Gmail integration** via OAuth to fetch and process inbox messages.
- **Secrets in the environment** — no API keys or credentials in the source.
- **Optional HTTP Basic auth** for the admin and Gmail routes.

---

## Architecture (MVC)

| Layer | Responsibility | Files |
|-------|----------------|-------|
| **Model** | Data access and domain logic | `app/model/database.py`, `app/model/contact_repository.py`, `app/model/extractor.py`, `app/model/gmail_service.py`, `app/model/schemas.py` |
| **View** | Templates and static assets | `app/view/templates/`, `app/view/static/` |
| **Controller** | HTTP routes | `app/controller/extraction_controller.py`, `app/controller/gmail_controller.py` |
| **App** | Factory, config, security | `app/main.py`, `app/config.py`, `app/security.py` |

```
email-extraction-ai/
├── app/
│   ├── main.py                       # App factory (uvicorn app.main:app)
│   ├── config.py                     # Environment-driven settings
│   ├── security.py                   # Admin HTTP Basic auth dependency
│   ├── model/
│   │   ├── database.py               # Connection + schema
│   │   ├── contact_repository.py     # Contact persistence
│   │   ├── extractor.py              # LLM extraction (Groq/LangChain)
│   │   ├── gmail_service.py          # Gmail OAuth + message retrieval
│   │   └── schemas.py                # Pydantic schemas
│   ├── view/
│   │   ├── templates/                # index, result, admin, emails
│   │   └── static/                   # style.css
│   └── controller/
│       ├── extraction_controller.py  # /, /extract, /api/extract, /admin
│       └── gmail_controller.py       # /authorize, /oauth2callback, /emails
├── requirements.txt
├── Procfile
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting started

### 1. Install

```bash
git clone https://github.com/MuziSan07/email-extraction-ai.git
cd email-extraction-ai

python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY (and admin credentials if desired)
```

Get a Groq API key at <https://console.groq.com>.

### 3. Run

```bash
uvicorn app.main:app --reload
```

- Home / extractor: <http://127.0.0.1:8000/>
- Admin panel: <http://127.0.0.1:8000/admin>
- Interactive API docs: <http://127.0.0.1:8000/docs>

---

## API reference

### `POST /api/extract`

```json
{ "email_content": "Hi, I'm John Smith from TechCorp. john@techcorp.com ..." }
```

Returns the extracted fields:

```json
{
  "name": "John Smith",
  "title": "",
  "company": "TechCorp",
  "email": "john@techcorp.com",
  "phone": "",
  "address": "",
  "website": "",
  "other_info": ""
}
```

### Web routes

- `GET /` — extractor form
- `POST /extract` — extract and save (form submission)
- `GET /admin` — admin panel (protected when admin auth is enabled)
- `DELETE /api/contact/{id}` — delete a contact (protected)

### Gmail routes (optional, protected)

- `GET /authorize` — begin Google OAuth
- `GET /oauth2callback` — OAuth redirect target
- `GET /emails` — fetch recent inbox messages and extract from them

---

## Gmail integration setup

1. Create an OAuth client (Desktop or Web) in the
   [Google Cloud Console](https://console.cloud.google.com/) and enable the
   Gmail API.
2. Download the client secrets as `credentials.json` into the project root
   (it is git-ignored).
3. Add `http://localhost:8000/oauth2callback` as an authorized redirect URI.
4. For local development over HTTP, set `OAUTH_INSECURE_TRANSPORT=true`.
   Never enable this in production.
5. Start the app and visit `/authorize`.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | **Required.** Groq API key |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | LLM model id |
| `GROQ_TEMPERATURE` | `0` | Sampling temperature |
| `DB_PATH` | `business_contacts.db` | SQLite database path |
| `MAX_EMAIL_LENGTH` | `20000` | Max characters accepted per email |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | — | Enable admin HTTP Basic auth |
| `CORS_ORIGINS` | `localhost:8000,127.0.0.1:8000` | Comma-separated allow-list |
| `OAUTH_INSECURE_TRANSPORT` | `false` | Allow HTTP during OAuth (dev only) |

---

## Security notes

- Secrets are read from the environment; never commit a real `.env`.
- The SQLite database and Google secrets (`credentials.json`, `token.json`) are
  git-ignored.
- Set admin credentials before exposing the admin or Gmail routes beyond local
  development.
- `OAUTH_INSECURE_TRANSPORT` must stay `false` outside local development.

---

## Tech stack

- **Backend:** FastAPI, Uvicorn
- **AI extraction:** LangChain + Groq
- **Storage:** SQLite
- **Frontend:** server-rendered Jinja2 templates
- **Email:** Gmail API (optional)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.
