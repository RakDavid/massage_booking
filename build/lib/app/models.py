"""Adatbázis modellek a masszázs időpontfoglaló alkalmazáshoz."""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app.extensions import db


# pylint: disable=too-few-public-methods
class User(db.Model, UserMixin):
    """Felhasználói modell, amely támogatja az autentikációt."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    bookings = db.relationship('Booking', backref='user', lazy=True)

    def check_password(self, password):
        """Ellenőrzi a megadott jelszót a hash alapján."""
        return check_password_hash(self.password, password)


class MassageService(db.Model):
    """Masszázs szolgáltatás modell."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(300))


class Booking(db.Model):
    """Foglalás modell."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
