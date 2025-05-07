import os
import shutil
from datetime import datetime
from app import create_app, db
from app.models import User, MassageService, Booking
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url


load_dotenv()


db_url = os.getenv("DATABASE_URL", "sqlite:///instance/db.sqlite3")
url_obj = make_url(db_url)


if url_obj.drivername == "sqlite":
    db_path = url_obj.database
    if os.path.exists(db_path):
        backup_path = f"{db_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(db_path, backup_path)
        print(f"📦 Biztonsági mentés készült: {backup_path}")


app = create_app()


with app.app_context():
    db.create_all()

    if not User.query.first():
        admin = User(
            name="Admin",
            email="admin@gmail.hu",
            password=generate_password_hash("admin1"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin felhasználó létrehozva (admin@gmail.hu / admin1)")
    else:
        print("Már vannak felhasználók – admin nem lett újra létrehozva.")

    print("Adatbázis inicializálva.")
