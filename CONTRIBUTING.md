<div align="center">

# 🤝 Contributing to CampusResolve

Thank you for considering a contribution to CampusResolve!  
This document is your **complete guide** to contributing effectively — from setting up your environment to getting your pull request merged.

> We welcome contributions of all sizes — from fixing a typo in a comment to adding an entire new feature.  
> **Every contribution matters.**

</div>

---

## 📌 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
- [Before You Start](#-before-you-start)
- [Development Setup](#-development-setup)
- [Project Architecture Overview](#-project-architecture-overview)
- [Branching Strategy](#-branching-strategy)
- [Coding Standards](#-coding-standards)
- [Writing & Running Tests](#-writing--running-tests)
- [Commit Message Guidelines](#-commit-message-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Reporting Bugs](#-reporting-bugs)
- [Requesting Features](#-requesting-features)
- [Environment Variables Reference](#-environment-variables-reference)
- [Getting Help](#-getting-help)

---

## 📜 Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and constructive environment for everyone. Specifically:

- **Be respectful** in all interactions — in code reviews, issues, and discussions.
- **Be constructive** — critique the code, never the person.
- **Be patient** — maintainers are students with coursework. Responses may take a few days.
- **Be inclusive** — we welcome contributors regardless of experience level. If you're new to open source, this is a great place to start.

Harassment, discrimination, or dismissive behaviour of any kind will not be tolerated and may result in being removed from the project.

---

## 💡 How Can I Contribute?

There are many ways to contribute beyond writing code:

| Type | Examples |
|:---|:---|
| 🐛 **Bug Reports** | Found an endpoint returning wrong data? Spotted a security issue? |
| ✨ **Feature Requests** | Have an idea that would improve the portal for students or admins? |
| 🔧 **Code Contributions** | Bug fixes, new endpoints, performance improvements, refactoring |
| 📖 **Documentation** | Improve the README, add docstrings, write API usage examples |
| 🧪 **Tests** | We have no tests yet — adding them is one of the highest-value contributions |
| 🎨 **Code Quality** | Improving error messages, cleaning up duplicated logic, adding type hints |

---

## ⚠️ Before You Start

Before spending time on a significant change, **open an issue first**.

This is important because:
- The maintainers might already be working on it
- The direction of the feature might need discussion
- You might get useful context that saves you hours of work

For **small fixes** (typos, broken links, obvious bugs), you can skip the issue and go straight to a pull request.

---

## 🛠️ Development Setup

Follow these steps exactly to get your local environment working.

### 1. Fork and Clone

```powershell
# [TERMINAL] Fork the repo on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/campusresolve-backend.git
cd campusresolve-backend

# Add the original repo as "upstream" so you can pull future changes
git remote add upstream https://github.com/ORIGINAL_ORG/campusresolve-backend.git
```

### 2. Create a Virtual Environment

```powershell
# [TERMINAL] Always use a virtual environment — never install globally
python -m venv venv
.\venv\Scripts\Activate.ps1

# You should see (venv) in your terminal prompt now
```

### 3. Install Dependencies

```powershell
# [TERMINAL] Install everything pinned to exact versions
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```powershell
# [TERMINAL] Copy the template
copy .env.example .env

# Now open .env and fill in your actual values
# See the Environment Variables Reference section below
```

You will need:
- A free [Cloudinary](https://cloudinary.com) account (for file upload testing)
- A free [Resend](https://resend.com) account (for email testing)
- PostgreSQL — either installed locally or via Docker (see step 5)

### 5. Start the Database

**Option A (Docker — recommended):**
```powershell
# [TERMINAL] This starts only the database, not the full app
docker compose up db -d
```

**Option B (local PostgreSQL):**
```powershell
# [TERMINAL] Create the database manually
# Connect to your local psql and run:
# CREATE DATABASE complaint_db;
# Then set DATABASE_URL in your .env to point to it
```

### 6. Run the Development Server

```powershell
# [TERMINAL] Hot-reload enabled by default
python run.py
```

✅ Confirm it works: open `http://localhost:8000/docs` in your browser. You should see the Swagger UI.

---

## 🏗️ Project Architecture Overview

Before writing any code, understand how the project is structured:

```
app/
├── api/
│   ├── auth.py          ← All signup/login logic + verify_token()
│   ├── complaints.py    ← Core business logic (raise, update, close complaints)
│   ├── students.py      ← Student profile endpoint
│   └── admin.py         ← Admin profile endpoint
│
├── config.py            ← Environment loading, logging, Sentry init
│                          (Add new env vars here — nowhere else)
│
├── database.py          ← SQLModel engine + get_session() dependency
│                          (Don't put queries here — keep them in api/ files)
│
├── model.py             ← All database table definitions (SQLModel)
│                          and Pydantic request schemas
│                          (Add new tables or schemas here)
│
├── cloudinary_helper.py ← Single upload_file() function
│                          (Don't call cloudinary directly elsewhere)
│
├── email_helper.py      ← One function per email type
│                          (Keep HTML templates here, not in api/ files)
│
└── main.py              ← App factory only
                           (No business logic here — just router registration)
```

**The rule of thumb:** each file has one responsibility. If you are unsure where code belongs, ask in your issue or PR.

### Key Patterns Used

**Dependency Injection** — FastAPI's `Depends()` is used for auth and DB sessions:
```python
# Every protected endpoint gets the token payload automatically
async def my_endpoint(token_payload: dict = Depends(verify_token),
                      session: Session = Depends(get_session)):
    ...
```

**Role Enforcement** — Always the first check in a protected handler:
```python
if token_payload.get("role") != "admin":
    raise HTTPException(status_code=403, detail="Unauthorized")
```

**Never return passwords** — Strip the password field before any response:
```python
return {
    "username": student.username,
    "college_email": student.college_email,
    # "password" is intentionally NOT included
}
```

---

## 🌿 Branching Strategy

We follow a simplified **GitHub Flow**:

```
main ────────────────────────────────────────────────► (production)
        │                           │
        └── feature/add-pagination  └── fix/student-stats-bug
             (your work happens here)
```

### Branch Naming Rules

Always branch off `main`. Use this naming format:

| Type | Format | Example |
|:---|:---|:---|
| New feature | `feature/short-description` | `feature/add-complaint-pagination` |
| Bug fix | `fix/short-description` | `fix/student-stats-counts-all` |
| Documentation | `docs/short-description` | `docs/add-api-examples` |
| Refactoring | `refactor/short-description` | `refactor/extract-email-service` |
| Tests | `test/short-description` | `test/add-auth-endpoint-tests` |

```powershell
# [TERMINAL] Always start from an up-to-date main
git checkout main
git pull upstream main

# Create and switch to your branch
git checkout -b feature/your-feature-name
```

> ⚠️ **Never commit directly to `main`.** All changes go through pull requests.

---

## ✍️ Coding Standards

Consistency makes the codebase easier for everyone to read and review. Follow these standards:

### Python Style

- Follow **PEP 8** — 4-space indentation, max 100 characters per line
- Use **type hints** on all function signatures:
  ```python
  # ✅ Good
  async def raise_complaint(title: str, token_payload: dict) -> Dict[str, str]:

  # ❌ Avoid
  async def raise_complaint(title, token_payload):
  ```
- Use **f-strings** for string formatting, not `.format()` or `%`
- Keep functions **short and focused** — if a function does more than one thing, split it

### Naming Conventions

| Element | Convention | Example |
|:---|:---|:---|
| Variables | `snake_case` | `complaint_id`, `student_username` |
| Functions | `snake_case` | `get_student_profile()` |
| Classes | `PascalCase` | `Student`, `ComplaintRequest` |
| Constants | `UPPER_SNAKE_CASE` | `SECRET_KEY`, `ALGORITHM` |
| Files | `snake_case` | `email_helper.py` |

### Docstrings

All new functions and endpoints **must** have a docstring. Use this format:

```python
async def close_complaint(complaint_id: str, ...) -> Dict[str, str]:
    """
    Closes a complaint with an admin-provided resolution document.

    Only accessible by administrators. The complaint must exist and must
    not already be in a 'closed' state. Triggers a closing email to
    the student upon success.

    Args:
        complaint_id: The UUID string of the complaint to close.
        closing_description: Admin's written explanation of the resolution.
        document: Resolution document file (PDF, image, etc.)
        token_payload: Decoded JWT payload — injected by verify_token().
        session: Database session — injected by get_session().

    Returns:
        Dict with 'message', 'complaint_id', and 'document_saved' (Cloudinary URL).

    Raises:
        HTTPException 403: If caller is not an admin.
        HTTPException 404: If complaint_id does not exist.
        HTTPException 400: If complaint is already closed.
    """
```

### FastAPI-Specific Rules

- **Never put business logic in `main.py`** — it's a factory only
- **Always use `Depends()`** for auth and DB sessions — never pass them manually
- **Set explicit `status_code`** on POST endpoints that create resources (`status_code=201`)
- **Use query parameters** for filtering (e.g., `?department=CSE`), not request bodies on GET
- **Log meaningful events** using the shared `logger` from `app.config`:
  ```python
  from app.config import logger
  logger.info(f"Student {username} raised complaint {complaint_id}")
  logger.warning(f"Failed login attempt for: {username}")
  logger.error(f"Unexpected error: {str(e)}", exc_info=True)
  ```

### What Not To Do

```python
# ❌ Don't hardcode secrets
SECRET = "my-secret-key"

# ❌ Don't catch and silently swallow exceptions
try:
    do_something()
except Exception:
    pass

# ❌ Don't return passwords in responses
return {"username": user.username, "password": user.password}

# ❌ Don't write queries outside of api/ files
# database.py is for session setup only

# ❌ Don't call cloudinary directly in endpoint handlers
# Use cloudinary_helper.upload_file() instead
```

---

## 🧪 Writing & Running Tests

> 🚧 The test suite is currently a high-priority area for contribution. If you'd like to add tests, that is extremely welcome.

### Setup

```powershell
# [TERMINAL] Install test dependencies
pip install pytest pytest-asyncio httpx
```

### Running Tests

```powershell
# [TERMINAL] Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific file
pytest tests/test_auth.py

# Run a specific test function
pytest tests/test_auth.py::test_student_signup_success
```

### Test File Structure

Place tests in a `tests/` directory mirroring the `app/api/` structure:

```
tests/
├── conftest.py          ← Shared fixtures (test client, test DB session)
├── test_auth.py         ← Tests for /auth/* endpoints
├── test_complaints.py   ← Tests for /complaints/* endpoints
├── test_students.py     ← Tests for /student/* endpoints
└── test_admin.py        ← Tests for /admin/* endpoints
```

### What to Test

Every new endpoint or behaviour change should include tests covering:

1. **Happy path** — Does it work correctly with valid input?
2. **Auth enforcement** — Does it return `403` when called without a token?
3. **Role enforcement** — Does a student get `403` on admin-only endpoints?
4. **Validation** — Does it return `422` or `400` for malformed input?
5. **Not found** — Does it return `404` for non-existent IDs?

### Example Test Structure

```python
# tests/test_complaints.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_raise_complaint_requires_student_role(client: AsyncClient, admin_token: str):
    """Admin token should be rejected when raising a complaint."""
    response = await client.post(
        "/complaints/complaint/raise",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={"title": "Test", "description": "Test", "department": "CSE", "phone_number": "9876543210"},
        files={"document": ("test.pdf", b"fake content", "application/pdf")}
    )
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_raise_complaint_success(client: AsyncClient, student_token: str):
    """Valid student token with all required fields should return 201."""
    response = await client.post(...)
    assert response.status_code == 201
    assert "complaint_id" in response.json()
```

---

## 💬 Commit Message Guidelines

Clear commit messages make the project history readable and help during debugging. We follow the **Conventional Commits** standard.

### Format

```
<type>(<scope>): <short summary>

[optional body — explain WHY, not WHAT]

[optional footer — breaking changes, closes #issue]
```

### Types

| Type | When to Use |
|:---|:---|
| `feat` | Adding a new feature or endpoint |
| `fix` | Fixing a bug |
| `docs` | Changes to documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `chore` | Build process, dependency updates, config changes |
| `perf` | Performance improvement |

### Scopes (for this project)

`auth` · `complaints` · `students` · `admin` · `email` · `cloudinary` · `db` · `config` · `docker` · `deps`

### Examples

```
feat(complaints): add pagination to admin complaint list endpoint

Adds skip and limit query parameters to GET /complaints/admin/my-complaints.
Without pagination, large departments could return thousands of records
in a single response, causing slow load times.

Closes #42
```

```
fix(complaints): student stats now filters by username

Previously, /complaint/student/stats was returning counts for ALL
complaints in the system, not just the authenticated student's own.
This was a data leak — any student could see total system stats.
```

```
docs(readme): update architecture diagram with email flow
```

### Rules

- **Use the imperative mood** — "add feature" not "added feature"
- **Keep the summary under 72 characters**
- **No period at the end** of the summary line
- **Reference issues** in the footer with `Closes #issue` or `Refs #issue`

---

## 🔁 Pull Request Process

### 1. Prepare Your Branch

```powershell
# [TERMINAL] Make sure your branch is up to date with main
git fetch upstream
git rebase upstream/main

# Stage and commit your changes
git add .
git commit -m "feat(complaints): add pagination to list endpoints"

# Push to your fork
git push origin feature/your-feature-name
```

### 2. Open the Pull Request

On GitHub, open a PR from your fork's branch into `upstream/main`. Fill out the template:

```markdown
## Summary
<!-- 2–3 sentences: what does this PR do and why? -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Tests

## Changes Made
- Added `skip` and `limit` query params to `/complaints/admin/my-complaints`
- Updated docstring on `get_admin_complaints()`
- Added two tests in `tests/test_complaints.py`

## How to Test
1. Start the server: `python run.py`
2. Login as admin, copy token
3. `GET /complaints/admin/my-complaints?skip=0&limit=10`
4. Should return max 10 results

## Related Issues
Closes #42

## Checklist
- [ ] Code follows project coding standards
- [ ] Docstrings added to all new functions
- [ ] Tests added (or explained why not applicable)
- [ ] README updated if endpoints or config changed
- [ ] Commits follow Conventional Commits format
- [ ] No new hardcoded secrets or credentials
```

### 3. Review Process

- A maintainer will review within **3–5 days**
- Address all review comments and push new commits
- **Do not force-push** after a review has started
- Once approved, a maintainer will merge

### 4. After Merging

```powershell
# [TERMINAL] Clean up your local branch
git checkout main
git pull upstream main
git branch -d feature/your-feature-name
```

---

## 🐛 Reporting Bugs

Good bug reports save maintainers hours. Please include:

**1. Environment Information**
```
OS: Windows 11
Python: 3.11.4
FastAPI: 0.135.3
Database: PostgreSQL 15 (Docker)
```

**2. Steps to Reproduce — be exact**
```
1. POST /auth/login/student with valid credentials → get token
2. GET /complaints/complaint/student/stats with Bearer token
3. Response shows total=47, but I only have 3 complaints
```

**3. Expected vs Actual Behaviour**
```
Expected: Stats should only count MY complaints (3 total)
Actual: Stats return counts for ALL complaints in the system
```

**4. Relevant Logs** — Paste output from terminal or `logs/app.log`. Remove credentials before posting.

**5. Security vulnerabilities** — Do NOT open a public issue. Email maintainers directly so the issue can be patched before disclosure.

---

## 💡 Requesting Features

1. **Check existing issues first** — it may already be planned
2. **Describe the problem, not just the solution** — "Students have no way to follow up on a closed complaint" is more useful than "Add a reopen button"
3. **Explain the use case** — who benefits and how?
4. **Consider the scope** — small addition or significant redesign?

Use the GitHub Issues tab and apply the `enhancement` label.

---

## 🔑 Environment Variables Reference

| Variable | Required | Description |
|:---|:---:|:---|
| `SECRET_KEY` | ✅ | JWT signing key — min 32 chars. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | ✅ | JWT algorithm. Use `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Token lifetime in minutes. Default: `30` |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `CLOUDINARY_CLOUD_NAME` | ✅ | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | ✅ | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | ✅ | From Cloudinary dashboard |
| `RESEND_API_KEY` | ✅ | From Resend dashboard |
| `RESEND_FROM_EMAIL` | ✅ | Verified sender email address |
| `SENTRY_DSN` | ❌ | Sentry project DSN. Leave blank to disable |
| `ENVIRONMENT` | ❌ | `development` or `production`. Default: `production` |

---

## 🆘 Getting Help

- **GitHub Issues** — Open an issue with the `question` label for setup or usage questions
- **PR Descriptions** — If your PR is complex, request an early review and explain your approach

When asking for help, always include: what you were trying to do, what you expected, what actually happened (with logs), and what you've already tried.

---

<div align="center">

Thank you for reading this far and for investing your time into CampusResolve. 🙏  
Every contribution, big or small, makes this project better for students everywhere.

**Happy coding!**  
*— Web Wizards Team, NIT Silchar*

</div>
