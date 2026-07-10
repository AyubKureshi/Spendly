# Spec: Registration

## Overview
Wire up the existing `/register` route so users can create a Spendly account. The form, page, and `users` table are already in place — this step adds the POST handler that validates input, hashes the password with `werkzeug`, inserts the user, logs them in with a Flask session, and redirects to the profile placeholder. This unlocks the rest of the auth flow (login/logout in step 3) and any feature that requires an authenticated session.

## Depends on
- Step 1 — Database setup (the `users` table with `id`, `name`, `email`, `password_hash` must exist; `get_db()` and `werkzeug.security` must be available)

## Routes
- `GET  /register`  — render `register.html` — public
- `POST /register`  — validate form, create user, start session, redirect — public

## Database changes
No schema changes. The `users` table created in step 1 already has the columns this step needs (`id`, `name`, `email UNIQUE`, `password_hash`, `created_at`).

## Templates
- **Modify:** `templates/register.html`
  - Pre-fill `name` and `email` fields with the submitted values when validation fails (so the user does not retype everything)
  - No structural markup changes; the existing form already POSTs to `/register` and renders `{{ error }}`

## Files to change
- `app.py` — convert `/register` from a single GET view to a GET/POST view; import `request`, `redirect`, `url_for`, `session` from Flask and `generate_password_hash` from `werkzeug.security`; import `get_db` from `database.db`; add a `SECRET_KEY` on the Flask app so sessions work.
- `templates/register.html` — preserve user input on validation failure (re-render with `name` and `email`).

## Files to create
None.

## New dependencies
No new pip packages. `werkzeug` and `flask` are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` from the standard library via `database.db.get_db()`.
- All SQL must be parameterised (`?` placeholders). Never interpolate user input into a query string.
- Passwords must be hashed with `werkzeug.security.generate_password_hash` before storage — never store plaintext.
- Use the `users.UNIQUE` constraint on `email` to surface a clean "Email already registered" error rather than crashing on `IntegrityError`.
- Use CSS variables for any new styles — never hardcode hex values in `static/css/style.css`.
- All templates must extend `base.html` (already true for `register.html`).
- Session management requires `app.secret_key` to be set. Use a dev-safe default (e.g. read from env, fall back to a hardcoded dev string) and call this out in a comment so it is replaced before production.
- Validation rules (server-side):
  - `name`: required, trimmed, 1–80 chars.
  - `email`: required, must match a basic email pattern (`@` and `.`), max 120 chars.
  - `password`: required, minimum 8 characters.
  - On any failure: re-render `register.html` with `error` and the original `name` / `email` values, return HTTP 400.
- On success: insert the user, set `session["user_id"]` and `session["user_name"]`, then `redirect(url_for("profile"))`.
- Do not implement login or logout in this step — they belong to step 3.

## Definition of done
- [ ] `GET /register` renders the form as before.
- [ ] `POST /register` with valid input creates a new row in `users` and redirects to `/profile`.
- [ ] The new user's `password_hash` is a `werkzeug` hash, not plaintext (verify by inspecting the row).
- [ ] `POST /register` with a missing name, invalid email, or password under 8 chars re-renders the form with the error message and the original `name`/`email` preserved.
- [ ] `POST /register` with an already-registered email shows "Email already registered" (or equivalent) and does not create a duplicate row.
- [ ] After successful registration, hitting any logged-in route (e.g. `/profile`) recognises the session.
- [ ] `app.secret_key` is set so the session cookie is signed.
- [ ] No hardcoded hex colours introduced; any new styles use existing CSS variables.
- [ ] App starts without errors via `python app.py` and the registration flow can be exercised end-to-end in a browser.
