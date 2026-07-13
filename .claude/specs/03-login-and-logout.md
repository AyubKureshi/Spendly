# Spec: Login and Logout

## Overview
Wire up the existing `/login` route and the placeholder `/logout` route so users can authenticate into Spendly and end their session. `/login` already renders a form; this step adds the POST handler that verifies credentials against the `users` table (using `werkzeug`'s password check) and starts a Flask session. `/logout` clears that session and bounces the user back to the landing page. The `SECRET_KEY`, `session["user_id"]`, and `session["user_name"]` keys were already introduced in step 2 — this step is where they get exercised for real, completing the auth loop (register → login → use app → logout).

## Depends on
- Step 1 — Database setup (the `users` table with `email` and `password_hash` must exist; `get_db()` must be available).
- Step 2 — Registration (the POST handler, `SECRET_KEY`, and the `session["user_id"]` / `session["user_name"]` keys this step writes to).

## Routes
- `POST /login`  — validate input, look up user by email, verify password, start session, redirect — public (but anonymous — redirects logged-in users away)
- `GET  /logout` — clear the session, redirect to `/` — public (idempotent: no-op for anonymous users)

`GET /login` already renders `login.html`; this step leaves that view intact.

## Database changes
No schema changes. `users.id`, `users.email`, and `users.password_hash` (already populated by step 2) are the only columns this step reads.

## Templates
- **Modify:** `templates/login.html`
  - Preserve the submitted `email` when validation or login fails (so the user does not retype it). The password field is intentionally NOT re-filled.
  - No structural markup changes; the existing form already POSTs to `/login` and renders `{{ error }}`.
- **Modify:** `templates/base.html`
  - When the user is logged in (`session.user_id` is set), swap the nav's "Sign in" / "Get started" links for a "Hi, `<name>`" greeting plus a "Log out" link pointing to `/logout`. When logged out, keep the existing nav.

## Files to change
- `app.py`
  - Convert `/login` from a single GET view to a GET/POST view.
  - On GET: if a session is already active, `redirect(url_for("profile"))` (so signed-in users don't see the sign-in form).
  - On POST: read + trim `email` and `password`, validate (email required, password required), look up the user by `email`, verify with `werkzeug.security.check_password_hash`. On success, set `session["user_id"]` and `session["user_name"]`, then `redirect(url_for("profile"))`. On failure, re-render `login.html` with `error` and the submitted `email`, returning HTTP 400.
  - Convert `/logout` from a placeholder string to a real handler that calls `session.clear()` and `redirect(url_for("landing"))`.
  - Add `check_password_hash` to the `werkzeug.security` import.
- `templates/login.html`
  - Render `value="{{ email or '' }}"` on the email input when the page is re-shown after a failed attempt, and pass the submitted email through from the route.
- `templates/base.html`
  - Conditionally render nav links based on `session.get("user_id")`. The logged-in branch shows the user's name and a "Log out" link; the logged-out branch keeps the current "Sign in" / "Get started" links.

## Files to create
None.

## New dependencies
No new pip packages. `werkzeug` (for `check_password_hash`) and `flask` (for `session`) are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` from the standard library via `database.db.get_db()`.
- All SQL must be parameterised (`?` placeholders). Never interpolate user input into a query string.
- Password verification must use `werkzeug.security.check_password_hash` against the stored `password_hash` — never compare plaintext.
- Constant-time comparison comes for free from `check_password_hash`; do not roll a manual comparison.
- For unknown email and wrong password, surface the same generic error ("Invalid email or password") so the response does not reveal whether the email is registered.
- Use CSS variables for any new styles — never hardcode hex values in `static/css/style.css`.
- All templates must extend `base.html` (already true for `login.html`).
- `session.clear()` is acceptable; do not implement a server-side session store.
- The `GET /logout` route should work even if the user is anonymous (idempotent: just clear whatever's there and redirect). Do not require POST for logout — keep it a simple link from the nav.
- On `GET /login`, if a session is already active, redirect to `/profile` so logged-in users do not see the sign-in form.
- Do not implement any other auth-related features in this step (password reset, "remember me", rate limiting, etc. are out of scope).
- Do not modify the registration flow or the database schema.

## Definition of done
- [ ] `GET /login` while logged out renders `login.html` with an empty form.
- [ ] `GET /login` while logged in redirects to `/profile` (no form is shown).
- [ ] `POST /login` with a valid email + matching password sets `session["user_id"]` and `session["user_name"]` and redirects to `/profile`.
- [ ] `POST /login` with an unknown email re-renders the form with "Invalid email or password" and the submitted `email` preserved.
- [ ] `POST /login` with a known email and a wrong password re-renders the form with the same generic "Invalid email or password" error and the submitted `email` preserved (password field stays blank).
- [ ] `POST /login` with an empty email or empty password re-renders the form with a clear "Email and password are required" style error and returns HTTP 400.
- [ ] `GET /logout` clears `session["user_id"]` and `session["user_name"]` and redirects to `/` (the landing page).
- [ ] `GET /logout` while logged out still redirects to `/` (no crash, no error).
- [ ] After logging in, the nav on `base.html` shows a greeting with the user's name and a "Log out" link; after logging out, the nav reverts to "Sign in" / "Get started".
- [ ] The "Log out" link is rendered as a plain `<a href="/logout">` so the browser can hit it via GET — no JS required.
- [ ] No hardcoded hex colours introduced; any new styles use existing CSS variables.
- [ ] App starts without errors via `python app.py` and the full login → use app → logout flow can be exercised end-to-end in a browser.
