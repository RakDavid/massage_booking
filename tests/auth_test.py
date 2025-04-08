import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.user = User(
            name="Teszt Elek",
            email="teszt@example.com",
            password=generate_password_hash("valodi_jelszo")
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_new_user(self):
        response = self.client.post('/register', data={
            'name': 'Új Felhasználó',
            'email': 'uj@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Sikeres regisztráció!', html)
        user = User.query.filter_by(email='uj@example.com').first()
        self.assertIsNotNone(user)

    def test_register_duplicate_email(self):
        response = self.client.post('/register', data={
            'name': 'Valaki',
            'email': 'teszt@example.com',
            'password': 'valami123',
            'confirm_password': 'valami123'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Ez az e-mail már regisztrálva van.', html)

    def test_login_valid_user(self):
        response = self.client.post('/login', data={
            'email': 'teszt@example.com',
            'password': 'valodi_jelszo'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Sikeres bejelentkezés!', html)

    def test_login_invalid_user(self):
        response = self.client.post('/login', data={
            'email': 'nemletezik@example.com',
            'password': 'rosszjelszo'
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Hibás bejelentkezési adatok.', html)

if __name__ == '__main__':
    unittest.main()