# 🎓 Student Portal API

A **FastAPI** backend for a college student management system — handling student/admin authentication, complaint tracking, and profile management. Built with clean architecture, JSON-based file storage, and production-grade logging via Sentry.

---

## 📁 Project Structure

```
project/
├── app/
│   ├── config.py          # Environment config, logging setup, file path constants
│   ├── dependencies.py    # Shared JSON read/write helpers (used across all routers)
│   ├── main.py            # FastAPI app factory — middleware + router registration
│   ├── model.py           # Pydantic request/response models
│   ├── auth.py            # Student & Admin signup/login endpoints
│   ├── students.py        # Student profile management (WIP)
│   ├── complaints.py      # Complaint submission & tracking (WIP)
│   └── admin.py           # Admin management endpoints (WIP)
├── user_data/             # Auto-created at runtime (gitignored)
│   ├── students.json      # Student records
│   ├── admin.json         # Admin records
│   └── complaint.json     # Complaint records
├── logs/
│   └── app.log            # Rotating application log
├── requirements.txt
├── run.py                 # Dev server launcher (CLI args support)
└── .env                   # Environment variables (never commit this!)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| Validation | Pydantic v2 |
| Password Hashing | Passlib (bcrypt) |
| Storage | JSON flat files |
| Logging | Python `logging` + File rotation |
| Monitoring | Sentry SDK |
| Config | python-dotenv |

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment

```powershell
# [TERMINAL] - Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Install Dependencies

```powershell
# [TERMINAL]
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# .env
SENTRY_DSN=your_sentry_dsn_here       # Optional: remove line if not using Sentry
ENVIRONMENT=development
DATA_DIR=user_data                     # Where JSON data files are stored
```

> **Note:** `SENTRY_DSN` is optional. The app starts fine without it.

### 4. Run the Development Server

```powershell
# [TERMINAL] - Default: http://127.0.0.1:8000
python run.py

# Custom port
python run.py --port 8001

# Expose to local network (e.g., for mobile testing)
python run.py --host 0.0.0.0

# Disable hot-reload (use in production)
python run.py --no-reload
```

---

## 📡 API Reference

### Base URL
```
http://127.0.0.1:8000
```

### 🔐 Authentication — `/auth`

#### Register a Student
```http
POST /auth/signup/student
Content-Type: application/json

{
  "username": "john_doe",
  "college_email": "john@nitsilchar.ac.in",
  "password": "securepassword123",
  "sch_id": "2401001"
}
```

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "username": "john_doe"
}
```

---

#### Register an Admin
```http
POST /auth/signup/admin
Content-Type: application/json

{
  "username": "admin_user",
  "password": "adminpass"
}
```

---

#### Student Login
```http
POST /auth/login/user
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "User login successful",
  "role": "student",
  "token": "dummy-user-token"
}
```

---

#### Admin Login
```http
POST /auth/login/admin
Content-Type: application/json

{
  "username": "admin_user",
  "password": "adminpass"
}
```

---

### 🩺 Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "active",
  "timestamp": "2025-01-01T10:00:00+00:00",
  "version": "2.0.0"
}
```

---

### 📖 Interactive API Docs

Once the server is running, visit:

| Interface | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## 🗃️ Data Storage

This project uses **JSON flat files** instead of a database — perfect for prototyping and college projects.

The `user_data/` directory is **auto-created** on first run using a "lazy initialization" pattern:

```python
# From dependencies.py — files are only created when first accessed
if not path_obj.exists():
    if path_obj in [STUDENTS_FILE, ADMIN_FILE, COMPLAINT_FILE]:
        # Creates the file with an empty list []
        write_default_file(path_obj)
```

### Student Record Shape
```json
{
  "username": "john_doe",
  "college_email": "john@nitsilchar.ac.in",
  "sch_id": "2401001",
  "password": "$2b$12$...",
  "profile_pic": "uploads/default.jpg"
}
```

> **⚠️ Passwords are hashed** using `bcrypt` on student signup. Admin passwords are currently stored in plaintext — this is a known issue to fix (see Roadmap).

---

## 🔧 Configuration Reference

All configuration lives in `config.py`. Key constants:

| Constant | Description |
|---|---|
| `DATA_DIR` | Root directory for all JSON data files (env: `DATA_DIR`) |
| `STUDENTS_FILE` | Path to `students.json` |
| `ADMIN_FILE` | Path to `admin.json` |
| `COMPLAINT_FILE` | Path to `complaint.json` |
| `SENTRY_DSN` | Sentry error tracking DSN (optional) |

### Logging

Logs are written to both the console and `logs/app.log`. The logger is named `"Personal Dashboard"` and can be imported anywhere:

```python
from app.config import logger

logger.info("Something happened")
logger.error("Something went wrong", exc_info=True)
```

---

## 🏗️ Architecture Notes

### App Factory Pattern (`main.py`)

The FastAPI app is created inside a `create_app()` factory function. This is a standard pattern that makes it easier to create multiple app instances (e.g., for testing).

```python
# main.py
def create_app() -> FastAPI:
    app = FastAPI(...)
    app.add_middleware(CORSMiddleware, ...)
    app.include_router(auth_router)
    return app

app = create_app()   # ← Uvicorn targets this instance
```

### Shared Helpers (`dependencies.py`)

All file I/O is centralized in two functions:

- `read_json_file(path)` — Reads a JSON file; auto-creates it with `[]` if it's a known data file.
- `write_json_file(path, data)` — Serializes and writes data; returns `True/False` for error handling.

This means **no router ever touches the filesystem directly** — they all go through these helpers.

---

## 🛣️ Roadmap

- [ ] Hash admin passwords on signup (same as student flow)
- [ ] Replace dummy tokens with real JWT authentication
- [ ] Implement `students.py` — profile view & update endpoints
- [ ] Implement `complaints.py` — submit, list, resolve complaints
- [ ] Implement `admin.py` — admin dashboard endpoints
- [ ] Migrate from JSON flat files to SQLite or PostgreSQL
- [ ] Add input validation (e.g., password strength, SCH ID format)
- [ ] Write unit tests with `pytest`

---

## 🐛 Known Issues

| Issue | Location | Severity |
|---|---|---|
| Admin passwords stored as plaintext | `auth.py → signup_admin` | 🔴 High |
| Tokens are hardcoded dummy strings | `auth.py → login_*` | 🔴 High |
| No rate limiting on login endpoints | `auth.py` | 🟡 Medium |
| `complaints.py` and `students.py` are empty | — | 🟡 Medium |

---

## 📦 Requirements

```
fastapi>=0.110.0
uvicorn[standard]>=0.23.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv==1.2.1
passlib[bcrypt]
httpx>=0.27.0
sentry-sdk
requests>=2.31.0
python-multipart>=0.0.6
```

> **Note:** `logging` is part of Python's standard library — remove it from `requirements.txt` to avoid install warnings.

---

## 👤 Author

**1st Year ECE Student, NIT Silchar**
Building full-stack projects to learn React + FastAPI alongside engineering coursework.

---

*Built with FastAPI • Documented with ❤️*
