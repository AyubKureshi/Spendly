# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Spendly

A personal expense tracker web app — Indian Rupee (₹)-first, currently a Flask app being built up step-by-step as a tutorial. The "spendly" name, `◈` brand icon, and tagline ("Track every rupee. Own your finances.") are the established identity; copy and templates already use them.

## Stack

- **Flask 3.1.3** with **Werkzeug 3.1.6** (`app.py`)
- **Jinja2** templates in `templates/`
- **SQLite** via a `database/` package (currently stubbed — see below)
- **Plain CSS + vanilla JS** — no bundler, no npm, no framework. All styles in `static/css/style.css`, all JS in `static/js/main.js`
- **pytest 8.3.5** + **pytest-flask 1.3.0** for tests
- Google Fonts: DM Serif Display (display) + DM Sans (body) — loaded in `templates/base.html`

## Commands

```bash
# Activate venv (Windows)
venv\Scripts\activate

# Run dev server (port 5001, debug on)
python app.py
# Then open http://127.0.0.1:5001

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
pytest -v                    # verbose
pytest tests/test_x.py       # single test file
pytest -k test_name          # single test by name
```

## Architecture

```
app.py                # Flask app + ALL routes (no blueprints)
database/
  __init__.py         # empty
  db.py               # STUB — students implement get_db/init_db/seed_db
templates/
  base.html           # layout: nav, footer, blocks {title, head, content, scripts}
  landing.html        # hero + features + CTA + YouTube modal
  register.html       # POSTs to /register
  login.html          # POSTs to /login
  terms.html          # legal
  privacy.html        # legal
static/
  css/style.css       # all styles, single file
  js/main.js          # currently a placeholder comment
```

**Routes (in `app.py`):**

| Route | Status | Step |
|---|---|---|
| `/` | implemented (landing) | — |
| `/register` | GET renders form; POST not wired | — |
| `/login` | GET renders form; POST not wired | — |
| `/terms`, `/privacy` | implemented | — |
| `/logout` | placeholder string | 3 |
| `/profile` | placeholder string | 4 |
| `/expenses/add` | placeholder | 7 |
| `/expenses/<id>/edit` | placeholder | 8 |
| `/expenses/<id>/delete` | placeholder | 9 |

The step numbers in the comments are the tutorial's roadmap — when implementing a feature, look for the matching step number in the route comment.

## Tutorial-style codebase: what to expect

This is a teaching project. Many pieces are intentionally left as student exercises:

- `database/db.py` is a comment-only stub. It must grow to provide:
  - `get_db()` — SQLite connection with `row_factory` and foreign keys enabled
  - `init_db()` — `CREATE TABLE IF NOT EXISTS` for all tables
  - `seed_db()` — sample data for development
- `static/js/main.js` is a single comment line. Add frontend behavior here as features are built.
- Several routes return plain strings labeled "coming in Step N".
- No tests have been written yet, even though pytest is installed.

When implementing a step, follow the route's comment for the expected behavior. Don't go beyond the listed step unless asked.

## Conventions

**Templating:**
- Every page extends `base.html` and overrides `{% block content %}`.
- `{% block title %}` sets the page title.
- The base template loads Google Fonts, `static/css/style.css`, and `static/js/main.js`; pages can add to `{% block head %}` and `{% block scripts %}`.
- Brand string "Spendly" and `◈` icon appear in nav, footer, and the landing page — keep them consistent.

**Modals (landing page pattern):**
- Trigger button: `<a data-modal-open="how">See how it works</a>`
- Modal markup: `<div class="modal-backdrop" id="modal-{id}" data-modal hidden>...`
- Close via `data-modal-close`, Escape key, or backdrop click — handled by the IIFE at the bottom of `landing.html`. To reuse this pattern on another page, copy that IIFE.

**Forms:**
- The auth pages already POST to their own URL with `{% if error %}` rendering — wire the handlers in `app.py` to match.

**Database (when implemented):**
- Use the `database/` package; import like `from database import db` then call `db.get_db()` etc.
- The DB file (`spendly.db`) is gitignored.

**Currency / locale:**
- All amounts render as ₹ (Indian Rupee). Keep this when adding expense tables/summaries.

## Environment notes

- venv lives at `venv/` and is gitignored — recreate with `python -m venv venv` if needed.
- Dev server is on **port 5001** (not 5000), with `debug=True`. The YouTube modal's iframe `src` is reset on close to stop playback — keep this pattern when adding more modals.
- macOS-only `__pycache__`/`.DS_Store` artifacts are gitignored.
