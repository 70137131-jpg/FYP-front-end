"""
models.py — SQLAlchemy models for the ATIS application.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Operator")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"


class Inspection(db.Model):
    __tablename__ = "inspections"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    plate = db.Column(db.String(20), nullable=True)          # nullable for unreadable plates
    location = db.Column(db.String(200), nullable=False)
    camera = db.Column(db.String(20), nullable=True)          # e.g. CAM-002
    status = db.Column(db.String(10), nullable=False)          # "safe" or "unsafe"
    confidence = db.Column(db.Integer, nullable=False)         # 0–100
    defects = db.Column(db.String(300), nullable=True)         # comma-separated, e.g. "Tread Wear,Sidewall Damage"

    alerts = db.relationship("Alert", backref="inspection", lazy=True)

    @property
    def defect_list(self):
        """Return defects as a Python list."""
        if not self.defects:
            return []
        return [d.strip() for d in self.defects.split(",") if d.strip()]

    def __repr__(self):
        return f"<Inspection {self.id} {self.plate or '—'} {self.status}>"


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey("inspections.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")   # pending/acknowledged/escalated/resolved
    response = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Alert {self.id} {self.status}>"
