# Spec: Profile Page

## Overview
Replace the placeholder string returned by `/profile` with a real account page that shows the signed-in user their account details — name, email, member-since date — and a small set of spending stats derived from their `expenses` rows (total spent this month, total spent all-time, expense count). The page is the landing spot after login/registration and the natural anchor for the upcoming add/edit/delete expense flows (steps 7–9), so it also includes an "Add an expense" call-to-action. Access is locked down to logged-in users; anonymous visitors are redirected to `/login`.

## Depends on
- Step 1 — Database setup (`users` and `expenses` tables; `get_db()`).
- Step 2 — Registration (`session["user_id"]` and `session["user_name"]` are set on signup and on login).
- Step 3 — Login and Logout (the `session` keys the route reads; the redirect-to-login behaviour for anonymous users mirrors the existing auth conventions).

## Routes
- `GET /profile` — render `profile.html` with the signed-in user's account info and spending stats — logged-in only (anonymous users → redirect to `/login`)

No new routes. `POST /profile` and any edit-profile flow are out of scope for this step — name/email changes belong to a later step.

## Database changes
No schema changes. This step only **reads** from the `users` and `expenses` tables that step 1 already created:

- `users.id`, `users.name`, `users.email`, `users.created_at` — for the account card.
- `expenses.user_id`, `expenses.amount`, `expenses.date` — for the stats (count, all-time total, this-month total).

The "this month" stat filters on `expenses.date` using the first day of the current month in `YYYY-MM-DD` form (string comparison works because dates are stored as ISO strings).

## Templates
- **Create:** `templates/profile.html`
  - Extends `base.html`.
  - Hero/account card: large `Hi, <name>` greeting, a smaller email line, a "Member since <date>" line.
  - Stats row: three stat tiles — "This month" (₹ total for the current calendar month), "All time" (₹ lifetime total), "Expenses" (count of rows for this user).
  - "Add an expense" CTA linking to `/expenses/add` (still a placeholder at this step; the link should already be present so the user can see where step 7 will plug in).
  - "Log out" button is intentionally NOT duplicated here — `base.html` already exposes it in the nav. A small secondary "Sign out" link in the account card is fine but optional.
  - Empty-state copy: when the user has zero expenses, the stats should show `₹0` and `0` (not blank/hidden), and a short "No expenses yet — add your first one" hint should sit below the stats.
- **Modify:** `app.py` only (no template changes elsewhere).

## Files to change
- `app.py`
  - Convert `/profile` from a placeholder string to a real view.
  - At the top of the view, if `session.get("user_id")` is `None`, `return redirect(url_for("login"))`.
  - Otherwise, open a connection via `get_db()`, fetch the `users` row by `id`, and compute three stats with parameterised queries:
    - `SELECT id, name, email, created_at FROM users WHERE id = ?`
    - `SELECT COUNT(*) AS n, COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?` (all-time)
    - `SELECT COALESCE(SUM(amount), 0) AS month_total FROM expenses WHERE user_id = ? AND date >= ?` where the bound date is the first day of the current month (`YYYY-MM-DD`).
  - Close the connection in a `finally` block.
  - Format amounts as `₹<value>` (e.g. `₹1,234`) using a small Python helper or inline f-string; the rupee prefix is mandatory per CLAUDE.md conventions.
  - Format `created_at` as a readable date (e.g. `"13 July 2026"`) — store the formatted string in a template variable, not a Jinja-side filter, to keep logic out of the template.
  - Render `profile.html` with the user row and the three stats as separate variables (`user`, `month_total`, `all_time_total`, `expense_count`).

## Files to create
- `templates/profile.html`

## New dependencies
No new pip packages. Everything used (`sqlite3`, `flask.session`, `flask.redirect`, `flask.url_for`, `datetime`) is either stdlib or already imported.

## Rules for implementation
- No SQLAlchemy or any ORM — use `sqlite3` from the standard library via `database.db.get_db()`.
- All SQL must be parameterised (`?` placeholders). Never interpolate user input into a query string.
- Never expose `password_hash` to the template — only select the columns that the page actually needs.
- The view must be defensive: if the `session["user_id"]` points at a row that no longer exists (e.g. the user was deleted in dev), redirect to `/logout` instead of crashing with an unhelpful error. Treat "user row missing" the same as "not logged in".
- All money rendering uses `₹` (Indian Rupee) — never `$` or `Rs.` or any other symbol. Use a thousands separator (`1,234`) for readability.
- Use CSS variables for any new styles — never hardcode hex values in `static/css/style.css`. If new visual treatment is needed (e.g. stat tiles), prefer reusing existing classes (`.auth-card`, `.form-input`, etc.) and only add a small new block scoped to `.profile-*` selectors.
- All templates must extend `base.html` (true for the new `profile.html`).
- Do not implement edit-profile, change-password, or delete-account in this step — out of scope.
- Do not modify the registration, login, logout, or database code in this step.

## Definition of done
- [ ] `GET /profile` while logged in renders `profile.html` showing the user's name, email, "Member since" date, and three stats (this-month total, all-time total, expense count).
- [ ] All amounts on the page render with the `₹` prefix; the all-time total for the seeded `demo@spendly.com` user matches the sum of the 8 seed expenses (₹5,898).
- [ ] `GET /profile` while logged out redirects to `/login` (no profile content leaks in the response body).
- [ ] The session-only `password_hash` column is never sent to the template (verify by inspecting the rendered HTML — no `password_hash` substring, and the template variables are restricted to safe columns).
- [ ] If a logged-in session points at a non-existent user id, `/profile` redirects to `/logout` instead of raising.
- [ ] A user with zero expenses sees `₹0` for both totals, `0` for the count, and the empty-state hint.
- [ ] All three stats are produced by parameterised SQL queries (no f-strings inside SQL).
- [ ] The "Add an expense" CTA links to `/expenses/add` (the placeholder route) and is visible on the page.
- [ ] No hardcoded hex colours introduced; any new styles use existing CSS variables.
- [ ] App starts without errors via `python app.py` and the registration → profile → logout flow can be exercised end-to-end in a browser.
