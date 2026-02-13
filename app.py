from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, User, Inspection, Alert

app = Flask(__name__)
app.secret_key = "atis-secret-key-change-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///atis.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ── Routes ────────────────────────────────────────────────────


@app.route("/")
def index():
    """Redirect to login if not authenticated, otherwise to dashboard."""
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Serve the login page and handle authentication."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session["user"] = user.email
            session["role"] = user.role
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    """Main dashboard with live stats and recent inspections."""
    if "user" not in session:
        return redirect(url_for("login"))

    inspections = Inspection.query.order_by(Inspection.timestamp.desc()).limit(10).all()

    total = Inspection.query.count()
    safe = Inspection.query.filter_by(status="safe").count()
    unsafe = Inspection.query.filter_by(status="unsafe").count()
    pending_alerts = Alert.query.filter_by(status="pending").count()
    pass_rate = round((safe / total * 100), 1) if total > 0 else 0

    stats = {
        "total": total,
        "safe": safe,
        "unsafe": unsafe,
        "pending_alerts": pending_alerts,
        "pass_rate": pass_rate,
    }

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
    """Alerts page — query alerts joined with inspections."""
    if "user" not in session:
        return redirect(url_for("login"))

    alert_rows = (
        Alert.query
        .join(Inspection)
        .order_by(Alert.created_at.desc())
        .all()
    )
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
    """History page — all inspections ordered by date."""
    if "user" not in session:
        return redirect(url_for("login"))

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
    """Reports page — generate and export inspection statistics."""
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("reports.html", user=session["user"], role=session["role"])


@app.route("/inspection/<int:inspection_id>")
def inspection_detail(inspection_id):
    """Detail page for a single inspection."""
    if "user" not in session:
        return redirect(url_for("login"))

    insp = Inspection.query.get_or_404(inspection_id)
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
    """Clear the session and return to login."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/predict", methods=["POST"])
def predict():
    """Handle prediction requests from the frontend."""
    if "user" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() if request.is_json else request.form.to_dict()
    result = {
        "success": True,
        "prediction": None,
        "message": "Prediction endpoint ready — connect your ML model here.",
    }
    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """Custom 500 page."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
