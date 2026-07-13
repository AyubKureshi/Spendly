import os
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)


# Dev-safe session signing key. Replace via env var before any production
# deployment — a hardcoded key here is acceptable for local development only.
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-only-change-me")


def _inr(value):
    """Format a number as ₹<value> with thousands separators (e.g. 5898 -> ₹5,898)."""
    return f"₹{value:,.0f}"


def _pretty_date(iso_text):
    """Render an ISO 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD' string as '13 July 2026'.

    Uses lstrip('0') to drop the leading zero on the day of the month, so the
    output works on both POSIX (`%-d`) and Windows (`%#d` / `%d`).
    """
    date_part = iso_text.split(" ")[0]
    dt = datetime.strptime(date_part, "%Y-%m-%d")
    day = dt.strftime("%d").lstrip("0")
    return f"{day} {dt.strftime('%B %Y')}"


# Initialize the database schema and seed demo data before the first request.
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # POST: read and trim form values.
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    # Validate. Any failure -> re-render with 400, preserving name/email.
    if not name:
        return render_template(
            "register.html", error="Name is required.", name=name, email=email
        ), 400
    if len(name) > 80:
        return render_template(
            "register.html",
            error="Name must be 80 characters or fewer.",
            name=name,
            email=email,
        ), 400
    if not email or "@" not in email or "." not in email or len(email) > 120:
        return render_template(
            "register.html",
            error="Please enter a valid email address.",
            name=name,
            email=email,
        ), 400
    if len(password) < 8:
        return render_template(
            "register.html",
            error="Password must be at least 8 characters.",
            name=name,
            email=email,
        ), 400

    # Hash the password and insert. Catch UNIQUE(email) to surface a clean error.
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        try:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Email already registered",
                name=name,
                email=email,
            ), 400
    finally:
        conn.close()

    # Start the session and redirect to the (placeholder) profile page.
    session["user_id"] = user_id
    session["user_name"] = name
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # If user is already logged in, redirect to profile
        if session.get("user_id") is not None:
            return redirect(url_for("profile"))
        return render_template("login.html")

    # POST: process login form
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    # Validate input
    if not email:
        return render_template("login.html", error="Email is required.", email=email), 400
    if not password:
        return render_template("login.html", error="Password is required.", email=email), 400

    # Look up user by email
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        )
        user = cursor.fetchone()
    finally:
        conn.close()

    # Verify password
    if user is not None and check_password_hash(user["password_hash"], password):
        # Successful login
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    # Invalid credentials - show generic error (don't reveal whether email exists)
    return render_template(
        "login.html", error="Invalid email or password", email=email
    ), 400


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    # Clear the session and redirect to landing page
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    # Logged-out users get bounced to /login so the page content never leaks.
    if session.get("user_id") is None:
        return redirect(url_for("login"))

    conn = get_db()
    try:
        # Defensive column list: never select password_hash.
        user = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (session["user_id"],),
        ).fetchone()

        # Stale session (user row was deleted): clear it and bounce to landing.
        if user is None:
            session.clear()
            return redirect(url_for("logout"))

        # All-time count and total in a single round trip.
        stats = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(amount), 0) AS total "
            "FROM expenses WHERE user_id = ?",
            (session["user_id"],),
        ).fetchone()

        # "This month" = current calendar month; ISO strings sort lexicographically.
        month_start = datetime.now().strftime("%Y-%m-01")
        month_total_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS month_total "
            "FROM expenses WHERE user_id = ? AND date >= ?",
            (session["user_id"], month_start),
        ).fetchone()
    finally:
        conn.close()

    return render_template(
        "profile.html",
        user=user,
        month_total=_inr(month_total_row["month_total"]),
        all_time_total=_inr(stats["total"]),
        expense_count=stats["n"],
        member_since=_pretty_date(user["created_at"]),
        now_month=datetime.now().strftime("%B"),
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
