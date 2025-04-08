"""Alkalmazás inicializálása és konfigurációja."""

from flask import Flask
from .extensions import db, login_manager, mail
from .views import main
from .models import User


def create_app():
    """Létrehozza és konfigurálja a Flask alkalmazást."""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        """Betölti a felhasználót az adatbázisból az ID alapján."""
        return User.query.get(int(user_id))

    app.register_blueprint(main)

    return app
