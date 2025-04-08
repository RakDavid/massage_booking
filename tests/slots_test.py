import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from datetime import date, timedelta, datetime, time
from app import create_app, db
from app.models import Booking, User
from werkzeug.security import generate_password_hash

class FreeSlotsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Létrehozunk egy teszt usert és egy foglalást
        self.user = User(name='Teszt User', email='teszt@user.hu', password=generate_password_hash('teszt'))
        db.session.add(self.user)
        db.session.commit()

        # Holnapra egy foglalt időpont 10:00
        tomorrow = date.today() + timedelta(days=1)
        db.session.add(Booking(date=tomorrow, time='10:00', service='Relax', user_id=self.user.id))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_free_slots_api(self):
        response = self.client.get('/api/free_slots')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        data = response.get_json()
        self.assertIsInstance(data, list)

        for event in data:
            self.assertIn('title', event)
            self.assertIn('start', event)
            self.assertIn('url', event)

        # Ellenőrizheted azt is, hogy a "10:00" időpont nincs benne holnapra (mert blokkolva van)
        blocked_start = f"{(date.today() + timedelta(days=1)).isoformat()}T10:00"
        self.assertFalse(any(event['start'] == blocked_start for event in data))

if __name__ == '__main__':
    unittest.main()
