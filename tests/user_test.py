import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import create_app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.user = User(name="Teszt Elek", email="teszt@example.com", password="hashed")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        user = User.query.filter_by(email="teszt@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Teszt Elek")

    def test_user_admin_flag(self):
        self.assertFalse(self.user.is_admin)

    def test_duplicate_email_error(self):
        user2 = User(name="Másik", email="teszt@example.com", password="hashed2")
        db.session.add(user2)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
