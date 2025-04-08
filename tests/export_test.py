import sys
import os
import unittest
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Booking

class ExportICSTest(unittest.TestCase):
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

    def test_export_ics_includes_booking(self):
        self.login()
        tomorrow = date.today() + timedelta(days=1)
        booking = Booking(
            user_id=self.user.id,
            date=tomorrow,
            time='10:00',
            service='Relax'
        )
        db.session.add(booking)
        db.session.commit()

        response = self.client.get('/export_ics')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/calendar')

        data = response.data.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', data)
        self.assertIn('Relax', data)
        self.assertIn('SUMMARY:Relax', data)

if __name__ == '__main__':
    unittest.main()
