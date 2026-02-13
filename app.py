"""
ATIS - Automated Tire Inspection System
Main Application File (Flask)

This file handles all the web routes, database connections, and logic for the application.
It connects to the SQLite database and renders the HTML templates for the user.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, Inspection, Alert
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management (keep this safe in production!)
app.secret_key = "atis-secret-key-change-in-production"

# Database configuration
# We are using SQLite for simplicity. The database file will be created in the 'instance' folder.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///atis.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)


# -------------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------------

@app.route("/")
def index():
    """
    The root route.
    If the user is logged in, send them to the dashboard.
    If not, send them to the login page.
    """
    if "user" in session:
        return redirect(url_for("dashboard"))
    
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login Route.
    GET: Renders the login form.
    POST: Processes the login form data.
    """
    if request.method == "POST":
        # Get data from the form
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Check if user exists in the database
        user = User.query.filter_by(email=email).first()

        # Check password (in a real app, use hashing like bcrypt!)
        if user and user.password == password:
            # Login successful: store user in session
            session["user"] = user.email
            session["role"] = user.role
            return redirect(url_for("dashboard"))
        else:
            # Login failed
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    """
    Dashboard Route.
    Shows the main overview: inspection stats, recent inspections, and alerts.
    """
    # Security check: must be logged in
    if "user" not in session:
        return redirect(url_for("login"))

    # Fetch the 10 most recent inspections for the table
    inspections = Inspection.query.order_by(Inspection.timestamp.desc()).limit(10).all()

    # Calculate statistics for the top cards
    total = Inspection.query.count()
    safe = Inspection.query.filter_by(status="safe").count()
    unsafe = Inspection.query.filter_by(status="unsafe").count()
    pending_alerts = Alert.query.filter_by(status="pending").count()
    
    # Avoid division by zero
    pass_rate = 0
    if total > 0:
        pass_rate = round((safe / total * 100), 1)

    # Package stats into a dictionary
    stats = {
        "total": total,
        "safe": safe,
        "unsafe": unsafe,
        "pending_alerts": pending_alerts,
        "pass_rate": pass_rate,
    }

    # Fetch recent alerts for the notification dropdown (limit 5)
    recent_alerts = (
        Alert.query
        .join(Inspection)
        .order_by(Alert.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "index.html",
        user=session["user"],
        role=session["role"],
        inspections=inspections,
        stats=stats,
        recent_alerts=recent_alerts,
    )


@app.route("/alerts")
def alerts():
    """
    Alerts Page.
    Displays all alerts and allows filtering by status (Pending, Resolved, etc).
    """
    if "user" not in session:
        return redirect(url_for("login"))

    # Get all alerts, joined with inspection data to show plate numbers, etc.
    alert_rows = (
        Alert.query
        .join(Inspection)
        .order_by(Alert.created_at.desc())
        .all()
    )
    
    # Count how many are pending (for the badge)
    pending_count = Alert.query.filter_by(status="pending").count()

    return render_template(
        "alerts.html",
        user=session["user"],
        role=session["role"],
        alerts=alert_rows,
        pending_count=pending_count,
    )


@app.route("/history")
def history():
    """
    History Page.
    Shows a complete log of all inspections stored in the system.
    """
    if "user" not in session:
        return redirect(url_for("login"))

    # Fetch all inspections, newest first
    inspections = Inspection.query.order_by(Inspection.timestamp.desc()).all()
    total_count = len(inspections)

    return render_template(
        "history.html",
        user=session["user"],
        role=session["role"],
        inspections=inspections,
        total_count=total_count,
    )


@app.route("/reports")
def reports():
    """
    Reports Page.
    (Placeholder) Future feature for generating PDF/Excel reports.
    """
    if "user" not in session:
        return redirect(url_for("login"))
        
    return render_template("reports.html", user=session["user"], role=session["role"])


@app.route("/inspection/<int:inspection_id>")
def inspection_detail(inspection_id):
    """
    Inspection Detail Page.
    Shows full details for a specific inspection ID.
    """
    if "user" not in session:
        return redirect(url_for("login"))

    # Get the inspection or show 404 if not found
    insp = Inspection.query.get_or_404(inspection_id)
    
    # Also get any alerts related to this inspection
    related_alerts = Alert.query.filter_by(inspection_id=insp.id).order_by(Alert.created_at.desc()).all()

    return render_template(
        "inspection.html",
        user=session["user"],
        role=session["role"],
        inspection=insp,
        alerts=related_alerts,
    )


@app.route("/logout")
def logout():
    """
    Logs the user out by clearing the session.
    """
    session.clear()
    return redirect(url_for("login"))


@app.route("/predict", methods=["POST"])
def predict():
    """
    Prediction API Endpoint.
    This route receives data (image or sensor) and would run the ML model.
    Currently returns a dummy success response.
    """
    if "user" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    # Get JSON data or form data
    data = request.get_json() if request.is_json else request.form.to_dict()
    
    # TODO: Connect actual ML model here!
    result = {
        "success": True,
        "prediction": None,
        "message": "Prediction endpoint ready -- connect your ML model here.",
    }
    return jsonify(result)


# -------------------------------------------------------------------------
# ERROR HANDLERS
# -------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    """Show a custom 404 page when a URL is not found."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """Show a custom 500 page for internal server errors."""
    return render_template("500.html"), 500


# Main entry point
if __name__ == "__main__":
    app.run(debug=True, port=5000)
