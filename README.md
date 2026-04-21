<div align="center">

# 🎓 CampusResolve

### A Production-Ready College Complaint Management System

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Storage-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com)
[![Sentry](https://img.shields.io/badge/Sentry-Monitoring-362D59?style=for-the-badge&logo=sentry&logoColor=white)](https://sentry.io)

<br/>

> **Digitizing grievance redressal for college campuses** — students raise complaints with evidence,  
> admins resolve them with full audit trails, and everyone gets notified automatically.

<br/>

🏆 *Built by **Web Wizards** · NIT Silchar · Hackathon 2025*

<br/>

[📡 API Docs](#-api-reference) · [🚀 Quick Start](#-getting-started) · [🐳 Docker](#-docker-setup) · [☁️ Deploy](#️-deployment-render)

</div>

---

## 📌 Table of Contents

- [What Is This?](#-what-is-this)
- [Feature Overview](#-feature-overview)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Authentication Flow](#-authentication-flow)
- [Complaint Lifecycle](#-complaint-lifecycle)
- [API Reference](#-api-reference)
- [Data Models](#-data-models)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Docker Setup](#-docker-setup)
- [Deployment](#️-deployment-render)
- [Security Notes](#-security-notes)
- [Monitoring](#-monitoring)

---

## 🧭 What Is This?

**CampusResolve** eliminates the chaotic process of students raising complaints verbally or through paper forms. It replaces it with a structured, digital workflow that's transparent for students and manageable for department admins.

```
WITHOUT CampusResolve          WITH CampusResolve
─────────────────────          ──────────────────
Student walks to office   →    Student submits online (30 seconds)
Admin loses paper form    →    Complaint stored in PostgreSQL forever
No status updates         →    Email at every status change
No evidence trail         →    Documents uploaded to Cloudinary (permanent)
No accountability         →    Full audit log via Sentry + app.log
```

---

## ✨ Feature Overview

<div align="center">

| Feature | 👨‍🎓 Student | 👨‍💼 Admin |
|:---|:---:|:---:|
| Sign up & log in | ✅ | ✅ |
| Upload profile avatar (Cloudinary CDN) | ✅ | ✅ |
| View own profile | ✅ | ✅ |
| Raise complaint with supporting document | ✅ | ❌ |
| View own complaints | ✅ | ❌ |
| View personal complaint stats | ✅ | ❌ |
| Receive email on every status change | ✅ | ❌ |
| View department complaints | ❌ | ✅ |
| Filter complaints by department | ❌ | ✅ |
| Update complaint status | ❌ | ✅ |
| Close complaint with resolution document | ❌ | ✅ |
| Department stats dashboard | ❌ | ✅ |
| Email alert on new complaint received | ❌ | ✅ |

</div>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                                    │
│              React Frontend  /  Postman  /  Mobile App               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  HTTPS + Bearer Token
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                             │
│                                                                      │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────┐  ┌────────┐  │
│  │  /auth/*    │  │  /complaints/*   │  │ /student  │  │ /admin │  │
│  │  Signup     │  │  Raise / Track   │  │    /me    │  │   /me  │  │
│  │  Login      │  │  Update / Close  │  └───────────┘  └────────┘  │
│  │  JWT Issue  │  │  Stats           │                              │
│  └─────────────┘  └──────────────────┘                              │
│                                                                      │
│  Middleware: CORS  ·  Global Exception Handler  ·  Sentry           │
└───────┬──────────────────┬─────────────────┬────────────────────────┘
        │                  │                 │
        ▼                  ▼                 ▼
  ┌──────────┐      ┌────────────┐    ┌─────────────┐
  │PostgreSQL│      │ Cloudinary │    │  Resend API  │
  │          │      │            │    │             │
  │ Students │      │  Avatars   │    │ Email Alerts│
  │ Admins   │      │  Complaint │    │ to Students │
  │ Complaints      │  Docs      │    │ and Admins  │
  └──────────┘      │  Resolution│    └─────────────┘
                    │  Docs      │
                    └────────────┘
```

---

## 🔄 Complaint Lifecycle

```
  Student submits complaint
         │
         ▼
     ┌────────┐         ┌─────────────────────────────┐
     │  OPEN  │────────►│ Dept. Admin emailed instantly│
     └────┬───┘         └─────────────────────────────┘
          │ Admin reviews
          ▼
  ┌─────────────┐       ┌─────────────────────────────┐
  │ IN_PROGRESS │──────►│ Student emailed: "In Review" │
  └──────┬──────┘       └─────────────────────────────┘
         │ Admin resolves
         ▼
    ┌──────────┐         ┌──────────────────────────────┐
    │ RESOLVED │────────►│ Student emailed: "Resolved"   │
    └────┬─────┘         └──────────────────────────────┘
         │ Admin formally closes with resolution document
         ▼
     ┌────────┐          ┌──────────────────────────────────────┐
     │ CLOSED │─────────►│ Student emailed with resolution note  │
     └────────┘          └──────────────────────────────────────┘
```

> ⚠️ Status transitions are **admin-only** and **append-only** — a closed complaint cannot be reopened.  
> Students receive a **transactional email** at every transition automatically via Resend.

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|:---|:---|:---|
| 🌐 Framework | **FastAPI 0.135** | Async REST API, auto-generated Swagger/ReDoc docs |
| 🗄️ Database | **PostgreSQL 15 + SQLModel** | Production relational DB with type-safe ORM |
| 🔄 Migrations | **Alembic** | Version-controlled, safe schema evolution |
| 🔐 Auth | **PyJWT + bcrypt 5** | Stateless JWT tokens, industry-standard password hashing |
| 📁 File Storage | **Cloudinary** | Permanent CDN URLs — no local disk, no broken links |
| 📧 Email | **Resend** | Reliable transactional email with HTML templates |
| 🔍 Monitoring | **Sentry SDK** | Real-time error capture, performance tracing |
| 📋 Logging | **Python `logging`** | Dual output — console stream + persistent `app.log` file |
| ⚡ Server | **Uvicorn** | Production-grade ASGI server |
| 🐳 Containers | **Docker + Compose** | One-command reproducible dev environment |
| ✅ Validation | **Pydantic v2** | Request/response schema validation at the boundary |

</div>

---

## 🗂️ Project Structure

```
campusresolve-backend/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py              # Signup, login, JWT creation & verify_token()
│   │   ├── complaints.py        # Full complaint CRUD + stats
│   │   ├── students.py          # Student profile endpoint
│   │   └── admin.py             # Admin profile endpoint
│   │
│   ├── __init__.py
│   ├── config.py                # Env vars, logging setup, Sentry init
│   ├── database.py              # SQLModel engine, session factory, table init
│   ├── model.py                 # DB table models + Pydantic request schemas
│   ├── cloudinary_helper.py     # upload_file() abstraction → Cloudinary
│   ├── email_helper.py          # HTML email templates + Resend send calls
│   └── main.py                  # App factory, middleware, router registration
│
├── logs/                        # Auto-created — gitignored
│   └── app.log
│
├── alembic/                     # Database migration scripts
│   ├── env.py
│   └── versions/
│
├── docker-compose.yml           # Local dev: API + PostgreSQL together
├── Dockerfile                   # Production container (python:3.11-slim)
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # All Python dependencies pinned
├── run.py                       # CLI dev launcher (--port, --host, --reload)
├── .env                         # ⚠️ NEVER COMMIT — local secrets
├── .env.example                 # ✅ Commit this — template for contributors
└── .gitignore
```

---

## 🔐 Authentication Flow

This API uses **stateless JWT (JSON Web Token)** authentication. There is no server-side session storage — the token itself contains all the information needed.

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1 — Login                                                  │
│                                                                  │
│  POST /auth/login/student                                        │
│  Body: { username, college_email, password }                     │
│                     │                                            │
│                     ▼                                            │
│         Server queries PostgreSQL                                │
│         Verifies bcrypt hash                                     │
│                     │                                            │
│                     ▼                                            │
│  Response: { token: "eyJhbGci..." }                              │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────┐
│  STEP 2 — Every Protected Request                                │
│                                                                  │
│  GET /complaints/student/my-complaints                           │
│  Header: Authorization: Bearer eyJhbGci...                       │
│                     │                                            │
│                     ▼                                            │
│         verify_token() decodes JWT                               │
│         Extracts: { sub: "john_doe", role: "student" }          │
│         Role check passes → returns data                         │
└─────────────────────────────────────────────────────────────────┘
```

**Token Payload Structure:**
```json
{
  "sub": "john_doe",
  "role": "student",
  "exp": 1749123456
}
```

> 💡 **Why JWT?** No database lookup needed to verify identity on every request. The token is cryptographically signed with `SECRET_KEY` — any tampering invalidates it instantly.

---

## 📡 API Reference

> 📖 Interactive docs auto-generated by FastAPI:
> - **Swagger UI** → `http://localhost:8000/docs`
> - **ReDoc** → `http://localhost:8000/redoc`

### 🔑 Authentication — prefix: `/auth`

| Method | Endpoint | Auth | Body | Description |
|:---:|:---|:---:|:---|:---|
| `POST` | `/auth/signup/student` | ❌ | Form: `username, college_email, password, sch_id, avatar` | Register new student |
| `POST` | `/auth/signup/admin` | ❌ | Form: `username, email, password, id, department, avatar` | Register new admin |
| `POST` | `/auth/login/student` | ❌ | JSON: `username, college_email, password` | Login → JWT token |
| `POST` | `/auth/login/admin` | ❌ | JSON: `username, college_email, password` | Login → JWT token |

### 📝 Complaints — prefix: `/complaints`

| Method | Endpoint | Role | Description |
|:---:|:---|:---:|:---|
| `POST` | `/complaints/complaint/raise` | Student | Raise complaint (form: title, description, department, phone + document file) |
| `GET` | `/complaints/student/my-complaints` | Student | All your own complaints |
| `GET` | `/complaints/complaint/student/stats` | Student | Your complaint counts by status |
| `GET` | `/complaints/admin/my-complaints?department=X` | Admin | All complaints, filterable by department |
| `GET` | `/complaints/complaint/admin/stats?department=X` | Admin | Stats dashboard, filterable by department |
| `PATCH` | `/complaints/complaint/{id}/status` | Admin | Update status: `open` / `in_progress` / `resolved` |
| `POST` | `/complaints/complaint/{id}/close` | Admin | Close with description + resolution document |

### 👤 Profiles

| Method | Endpoint | Role | Returns |
|:---:|:---|:---:|:---|
| `GET` | `/student/me` | Student | Profile data (password excluded) |
| `GET` | `/admin/me` | Admin | Profile data (password excluded) |

### 🩺 System

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/health-status` | Heartbeat — returns `{ status, timestamp, version }` |

---

## 📦 Data Models

### 👨‍🎓 Student

```
┌──────────────────────────────────────────┐
│  Student (PostgreSQL table)              │
├──────────────────┬───────────────────────┤
│  id              │ INT (auto PK)         │
│  username        │ VARCHAR (unique)      │
│  college_email   │ VARCHAR (unique)      │
│  sch_id          │ VARCHAR               │
│  password        │ VARCHAR (bcrypt hash) │
│  profile_pic     │ VARCHAR (Cloudinary)  │
└──────────────────┴───────────────────────┘
```

### 👨‍💼 Admin

```
┌──────────────────────────────────────────┐
│  Admin (PostgreSQL table)                │
├──────────────────┬───────────────────────┤
│  id              │ INT (auto PK)         │
│  username        │ VARCHAR (unique)      │
│  email           │ VARCHAR (unique)      │
│  admin_id        │ VARCHAR               │
│  department      │ VARCHAR               │
│  password        │ VARCHAR (bcrypt hash) │
│  profile_pic     │ VARCHAR (Cloudinary)  │
└──────────────────┴───────────────────────┘
```

### 📋 Complaint

```
┌───────────────────────────────────────────────┐
│  Complaint (PostgreSQL table)                  │
├──────────────────────┬────────────────────────┤
│  id                  │ UUID string (PK)        │
│  student_username    │ VARCHAR (indexed)       │
│  title               │ VARCHAR                 │
│  description         │ TEXT                    │
│  complaint_document  │ VARCHAR (Cloudinary URL)│
│  status              │ ENUM (4 values)         │
│  created_at          │ DATE string             │
│  department          │ VARCHAR                 │
│  phone_number        │ VARCHAR (10–15 chars)   │
│  closing_description │ TEXT (nullable)         │
│  closing_documents   │ VARCHAR (nullable)      │
└──────────────────────┴────────────────────────┘
```

**Status flow (append-only):**
```
"open"  →  "in_progress"  →  "resolved"  →  [admin close call]  →  "closed"
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Docker Desktop** (recommended) — or a local PostgreSQL installation
- Free accounts at: [Cloudinary](https://cloudinary.com) · [Resend](https://resend.com)
- Optional: [Sentry](https://sentry.io) for error monitoring

---

### ⚡ Option A — Docker (Recommended)

No database setup required. One command starts everything.

```powershell
# [TERMINAL] 1. Clone the repository
git clone https://github.com/your-org/campusresolve-backend.git
cd campusresolve-backend

# [TERMINAL] 2. Create your environment file
copy .env.example .env
# Now open .env and fill in your actual secrets

# [TERMINAL] 3. Build and start
docker compose up --build
```

✅ API live at: `http://localhost:8000`  
✅ Swagger UI: `http://localhost:8000/docs`  
✅ PostgreSQL running at: `localhost:5432`

---

### 🔧 Option B — Manual Setup

```powershell
# [TERMINAL] 1. Clone and enter directory
git clone https://github.com/your-org/campusresolve-backend.git
cd campusresolve-backend

# [TERMINAL] 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# [TERMINAL] 3. Install all dependencies
pip install -r requirements.txt

# [TERMINAL] 4. Set up your environment file
copy .env.example .env
# Edit .env with your actual secrets

# [TERMINAL] 5. Start the development server
python run.py
```

```powershell
# Optional flags for run.py:
python run.py --port 8001          # Different port
python run.py --host 0.0.0.0      # Listen on all interfaces
python run.py --no-reload          # Disable hot-reload (production mode)
```

---

## 🔧 Environment Variables

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env` to Git.**

```env
# ── Core Security ─────────────────────────────────────
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-super-secret-key-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ── Database ──────────────────────────────────────────
# Local:  postgresql://postgres:postgres@localhost:5432/complaint_db
# Render: postgresql://user:pass@host/dbname  (from Render dashboard)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/complaint_db

# ── Cloudinary (File Storage) ─────────────────────────
# Dashboard → https://console.cloudinary.com
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# ── Resend (Transactional Email) ──────────────────────
# Dashboard → https://resend.com/api-keys
# Note: verify your domain at resend.com/domains for production
RESEND_API_KEY=re_your_api_key
RESEND_FROM_EMAIL=noreply@yourdomain.com

# ── Sentry (Error Monitoring) — Optional ──────────────
# Leave blank to disable. Get DSN from sentry.io project settings.
SENTRY_DSN=
ENVIRONMENT=development
```

---

## 🐳 Docker Setup

The `docker-compose.yml` manages two containers:

```
┌──────────────────────────────────────────┐
│  docker-compose                          │
│                                          │
│  ┌──────────────┐    ┌────────────────┐  │
│  │  db service  │    │  api service   │  │
│  │  postgres:15 │◄───│  FastAPI app   │  │
│  │  port: 5432  │    │  port: 8000    │  │
│  │  (healthcheck│    │  (waits for db │  │
│  │   enabled)   │    │   to be ready) │  │
│  └──────────────┘    └────────────────┘  │
└──────────────────────────────────────────┘
```

**Common commands:**

```powershell
# [TERMINAL] Start everything (foreground, see logs)
docker compose up --build

# [TERMINAL] Start in background
docker compose up -d

# [TERMINAL] View API logs only
docker compose logs -f api

# [TERMINAL] Stop everything (keeps database data)
docker compose down

# [TERMINAL] Stop and wipe database (fresh start)
docker compose down -v

# [TERMINAL] Rebuild only the API image (after code changes)
docker compose build api && docker compose up -d api
```

> 💡 Database tables are created automatically on first startup via the `lifespan` event — no manual `CREATE TABLE` needed.

---

## ☁️ Deployment (Render)

This project ships with a production-ready `Dockerfile` for [Render](https://render.com).

```
Step 1 → Push code to GitHub

Step 2 → Render Dashboard → New → PostgreSQL
         Copy the "Internal Database URL"

Step 3 → Render Dashboard → New → Web Service
         ├── Connect GitHub repo
         ├── Runtime: Docker
         └── (Dockerfile is auto-detected)

Step 4 → Add Environment Variables in Render dashboard
         (all variables from the .env section above)

Step 5 → Deploy — Render builds the image and starts the container
```

**Production start command (inside Dockerfile):**
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

> ⚠️ Set `ENVIRONMENT=production` in Render env vars and restrict CORS `allow_origins` to your frontend domain.

---

## 🛡️ Security Notes

| Practice | Implementation |
|:---|:---|
| Password storage | `bcrypt` with random salt — plain text never stored or logged |
| Token security | JWT signed with `SECRET_KEY`, expires in 30 min |
| Role enforcement | Every protected endpoint checks `token_payload["role"]` before data access |
| Password in responses | Always stripped via `.pop("password", None)` or excluded in response dict |
| File storage | Uploads go directly to Cloudinary — no files stored on the server |
| CORS | Currently `allow_origins=["*"]` — **restrict to your frontend URL in production** |
| Secrets | All credentials in `.env`, never hardcoded, `.gitignore` enforced |

---

## 📊 Monitoring

### Sentry — Error Tracking

```
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment="production",
    traces_sample_rate=0.1,   ← 10% of requests traced for performance
    send_default_pii=False    ← No personal data sent to Sentry
)
```

Captured automatically:
- ✅ All unhandled exceptions with full stack trace
- ✅ Failed login attempts (`warning` level)
- ✅ File write errors in dependencies
- ✅ Any `sentry_sdk.capture_exception(e)` call

### Application Logging

All log events are written to **two destinations simultaneously**:

```
Console (stdout)  →  Visible in Docker logs / Render log stream
logs/app.log      →  Persistent file on disk (auto-created, gitignored)
```

Log format:
```
HH:MM:SS - Personal Dashboard - INFO - Student john_doe raised complaint abc-123
```

---

<div align="center">

## 👨‍💻 Built By

**Web Wizards Team** — National Institute of Technology Silchar  
*CampusResolve · Hackathon 2025*

<br/>

⭐ *If this project helped you, please star the repository!*

</div>
