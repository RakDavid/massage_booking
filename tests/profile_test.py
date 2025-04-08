import sys
import os
import unittest
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User

class ProfileUpdateTestCase(unittest.TestCase):
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

    def login(self):
        self.client.post('/login', data={
            'email': 'teszt@example.com',
            'password': 'valodi_jelszo'
        }, follow_redirects=True)

    def test_update_profile_correct_password(self):
        self.login()
        response = self.client.post('/update_profile', data={
            'name': 'Új Név',
            'email': 'uj@example.com',
            'current_password': 'valodi_jelszo',  
            'new_password': '' 
        }, follow_redirects=True)

        updated_user = User.query.filter_by(id=self.user.id).first()
        self.assertEqual(updated_user.name, 'Új Név')
        self.assertEqual(updated_user.email, 'uj@example.com')
        self.assertIn("Profil adatok sikeresen frissítve!", response.data.decode())

    def test_update_profile_wrong_password(self):
        self.login()
        response = self.client.post('/update_profile', data={
            'name': 'Valaki',
            'email': 'valaki@example.com',
            'current_password': 'rosszjelszo',
            'new_password': ''
        }, follow_redirects=True)

        user = User.query.filter_by(id=self.user.id).first()
        self.assertNotEqual(user.email, 'uj@example.com')
        self.assertIn("Hibás jelszó", response.data.decode())

if __name__ == '__main__':
    unittest.main()
