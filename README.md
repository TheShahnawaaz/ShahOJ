# ShahOJ (PocketOJ) — Multi-User Competitive Programming Judge

ShahOJ is a Flask-based, Codeforces-style online judge for creating, managing, and evaluating competitive programming problems using standard **stdin/stdout** workflows.

It supports:
- multi-user problem authoring,
- Google OAuth authentication,
- private/public problem visibility,
- configurable judge limits and checker modes,
- a web UI for authoring and submissions,
- optional AI-assisted content/code generation.

## Core Capabilities

- **Web platform for problem management**: create, edit, publish, and maintain problems from the browser.
- **Submission pipeline**: evaluate C++ submissions with verdicts such as AC/WA/TLE/CE.
- **Multiple checker modes**:
  - `diff` (exact text compare)
  - `float` (tolerance-based float compare)
  - `spj` (custom special judge)
- **Resource controls**: per-problem time and memory limits.
- **Multi-user + ownership model**:
  - Google OAuth login
  - per-problem author ownership
  - superuser override access
- **SQLite-backed metadata and submissions**.
- **Optional AI integration** via OpenAI-compatible endpoints.

---

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite
- **Judge target language:** C++ (g++)
- **Auth:** Google OAuth (Authlib)
- **Production serving:** Gunicorn + WSGI (`wsgi.py`)

---

## Quick Start (Local Development)

### 1) Prerequisites

- Python **3.10+** recommended
- `g++` with C++17 support
- `pip`

### 2) Install dependencies

```bash
cd /workspace/ShahOJ
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Configure environment

Create a `.env` file (or export directly):

```bash
# Required for secure sessions in real deployments
SECRET_KEY="replace-with-a-strong-secret"

# Optional: Google OAuth (required for login flow)
GOOGLE_CLIENT_ID="..."
GOOGLE_CLIENT_SECRET="..."

# Optional: AI features
OPENAI_API_KEY="..."
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_MODEL="gpt-4.1-mini"
OPENAI_MAX_TOKENS="6144"
```

> The app reads env vars through `python-dotenv` and config interpolation in `config.yaml`.

### 4) Start the app

```bash
python3 app.py
```

Default host/port are controlled by `config.yaml` (`web.host`, `web.port`).

---

## Production Run

`wsgi.py` exposes `application` and defaults `POCKETOJ_CONFIG` to `config.prod.yaml`.

Example:

```bash
gunicorn wsgi:application -k gevent -w 2 -b 0.0.0.0:8000
```

---

## Configuration

Main config files:
- `config.yaml` (development-oriented)
- `config.prod.yaml` (production-oriented)

Important keys:

- `system.problems_dir`: problem storage directory
- `system.default_time_limit_ms`: default TL
- `system.default_memory_limit_mb`: default ML
- `database.path`: SQLite DB file path
- `security.superusers`: list of admin emails
- `ai.*`: OpenAI-compatible provider settings

### Superusers

Configure through either:
- `security.superusers` in YAML config, or
- `POCKETOJ_SUPERUSERS` env var (comma-separated).

---

## Judge Usage (CLI)

The standalone judge can be invoked directly:

```bash
python3 judge/judge.py <problem_dir> <solution.cpp>
```

Help:

```bash
python3 judge/judge.py --help
```

---

## Repository Layout

```text
.
├── app.py                     # Flask app entry point (dev)
├── wsgi.py                    # Production WSGI entry
├── core/                      # Core services (auth, DB, config, jobs, judge helpers)
├── judge/                     # Standalone judge runtime and toolchain
├── templates/                 # Jinja templates
├── static/                    # CSS/JS/assets
├── problem_templates/         # Problem scaffolding/templates
├── migration/                 # Migration utilities for existing problem sets
├── scripts/                   # Operational scripts (e.g., clear submissions)
├── TUTORIAL/                  # Authoring and platform documentation
├── config.yaml
├── config.prod.yaml
└── requirements.txt
```

---

## Validation Performed

The following checks were run in this repository:

```bash
python3 -m compileall app.py core judge migration problem_templates scripts wsgi.py
python3 judge/judge.py --help
```

Both commands completed successfully in this environment.

---

## Operations Notes

- First run will initialize the SQLite database automatically.
- OAuth login requires valid Google credentials and callback configuration.
- If AI credentials are absent, AI-dependent actions will be unavailable, but core judging features still work.

---

## Learning Resources

For full problem authoring workflows, see:

- `TUTORIAL/README.md`
- `TUTORIAL/02-quick-start.md`
- `TUTORIAL/10-solution-testing.md`
- `TUTORIAL/14-ai-code-generation.md`

---

## License

This repository currently does not expose a top-level `LICENSE` file. Add one if you want explicit licensing terms.
