# 📋 Nexus Complaint Portal — Backend API

> A role-based complaint management system for college students and administrators, built with **FastAPI** and secured with **JWT authentication**.

---

## 🧭 What Is This?

The Nexus Complaint Portal is a REST API backend that lets students raise formal complaints to their college departments, and lets admins track, update, and close those complaints — all with proper role-based access control.

Think of it like a **digital suggestion/complaint box**, but smarter:
- Students can only see their own complaints
- Admins can only see complaints from their department
- Nobody can touch what they're not supposed to

---

## ✨ Feature Overview

| Feature | Student | Admin |
|---|---|---|
| Sign up & log in | ✅ | ✅ |
| Upload profile avatar | ✅ | ✅ |
| Raise a complaint with document | ✅ | ❌ |
| View own complaints | ✅ | ❌ |
| View department complaints | ❌ | ✅ |
| Update complaint status | ❌ | ✅ |
| Close complaint with resolution doc | ❌ | ✅ |
| View complaint stats dashboard | ✅ (own) | ✅ (by dept) |

---

## 🗂️ Project Structure

```
app/
├── api/
│   ├── auth.py          # Signup, login, JWT token creation
│   ├── complaints.py    # Raise, track, update, close complaints
│   ├── students.py      # Student profile endpoint
│   └── admin.py         # Admin profile endpoint
├── config.py            # Env vars, logging, Sentry setup
├── dependencies.py      # JSON file read/write helpers
├── model.py             # Pydantic request models
└── main.py              # App factory, router registration, middleware
```

---

## 🔄 How It All Flows

```
Client Request
     │
     ▼
 FastAPI App  (main.py)
     │
     ├──► /auth/*        ─► Signup / Login → returns JWT Token
     │
     ├──► /complaints/*  ─► Bearer Token required
     │         │
     │         ├── role == "student"  → can raise & view own complaints
     │         └── role == "admin"    → can manage & close complaints
     │
     ├──► /student/me    ─► Returns profile (student token only)
     └──► /admin/me      ─► Returns profile (admin token only)
```

---

## 🔐 Authentication Design

This API uses **JWT (JSON Web Tokens)** for stateless authentication.

When you log in, the server returns a token like:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

This token is **self-contained** — it holds your `username` and `role` inside it. Every protected endpoint decodes this token to know who you are and what you're allowed to do. No database lookup needed to check identity.

```
Login Request  →  Server checks credentials
                       │
                       ▼
               Creates token with:
               { "sub": "john_doe", "role": "student", "exp": ... }
                       │
                       ▼
               You send this token in every future request
               Authorization: Bearer <token>
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### 1. Clone & Install

```powershell
# [TERMINAL]
git clone <your-repo-url>
cd nexus-backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional
SENTRY_DSN=your-sentry-dsn
ENVIRONMENT=development
DATA_DIR=user_data
```

> ⚠️ **Never commit your `.env` file to GitHub.** Add it to `.gitignore`.

### 3. Run the Server

```powershell
# [TERMINAL]
uvicorn app.main:app --reload
```

The API will be live at: `http://127.0.0.1:8000`

---

## 📡 API Endpoints

### 🔑 Authentication  `prefix: /auth`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup/student` | Register a new student (multipart form + avatar) |
| `POST` | `/auth/signup/admin` | Register a new admin (multipart form + avatar) |
| `POST` | `/auth/login/student` | Login and receive JWT token |
| `POST` | `/auth/login/admin` | Login and receive JWT token |

### 📝 Complaints  `prefix: /complaints`

| Method | Endpoint | Who | Description |
|---|---|---|---|
| `POST` | `/complaints/complaint/raise` | Student | Raise a new complaint with a document |
| `GET` | `/complaints/student/my-complaints` | Student | List your own complaints |
| `GET` | `/complaints/admin/my-complaints?department=X` | Admin | List complaints by department |
| `GET` | `/complaints/complaint/admin/stats?department=X` | Admin | Stats dashboard |
| `GET` | `/complaints/complaint/student/stats` | Student | Stats dashboard |
| `PATCH` | `/complaints/complaint/{id}/status` | Admin | Update status (open/in_progress/resolved) |
| `POST` | `/complaints/complaint/{id}/close` | Admin | Close with a resolution document |

### 👤 Profiles

| Method | Endpoint | Who | Description |
|---|---|---|---|
| `GET` | `/student/student/me` | Student | Get your own profile |
| `GET` | `/admin/admin/me` | Admin | Get your own profile |

---

## 📦 Data Models

### Student Signup (Form Data)
```
username, college_email, password, sch_id, avatar (file)
```

### Complaint (JSON Body)
```json
{
  "student_username": "john_doe",
  "title": "No water in hostel",
  "description": "The water supply has been cut for 3 days...",
  "department": "Hostel",
  "phone_number": "9876543210"
}
```

### Complaint Status Flow
```
open  →  in_progress  →  resolved  →  [admin closes]  →  closed
```

---

## 🗄️ Storage

This project uses **flat JSON files** as a database — a great choice for prototyping and college projects.

| File | Stores |
|---|---|
| `user_data/students.json` | All registered students |
| `user_data/admin.json` | All registered admins |
| `user_data/complaint.json` | All complaints |
| `user_data/uploads/` | Profile avatars |
| `user_data/resolutions/` | Complaint & resolution documents |

> 💡 Files are **lazily initialized** — they get created automatically the first time they're needed. No manual setup required.

---

## 🔍 Interactive API Docs

FastAPI ships with built-in documentation. Once the server is running, open:

- **Swagger UI** → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — Try endpoints directly in the browser
- **ReDoc** → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) — Clean reference documentation

---

## 🛡️ Security Notes

- Passwords are hashed using **bcrypt** before storage — plain text passwords are never saved
- JWT tokens expire after 30 minutes (configurable)
- Role checks (`student` vs `admin`) are enforced on every protected endpoint
- The `password` field is stripped from all API responses before returning profile data

---

## 📊 Monitoring

This project integrates with **Sentry** for error tracking and performance monitoring in production.

- Failed login attempts are captured as warnings
- Unhandled exceptions are automatically reported
- All significant events are logged locally to `logs/app.log`

To enable Sentry, add `SENTRY_DSN` to your `.env` file.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Auth | JWT (PyJWT) + bcrypt |
| Validation | Pydantic v2 |
| Monitoring | Sentry SDK + Python logging |
| Storage | JSON flat files |
| Server | Uvicorn |

---

## 👨‍💻 Built By

**Web Wizards Team** — NIT Silchar  
*Nexus Dashboard Project — 2025*

---

## 📄 License

This project is for academic use. Feel free to fork and build on top of it.
