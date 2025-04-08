import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Booking, MassageService

class BookingFormTestCase(unittest.TestCase):
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

        self.service = MassageService(name="Relax", description="Relaxáló masszázs", price=10000)
        db.session.add(self.service)
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

    def test_successful_booking(self):
        self.login()
        response = self.client.post('/booking', data={
            'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'service': self.service.name
        }, follow_redirects=True)
        self.assertIn('Sikeres foglalás!', response.data.decode('utf-8'))

    def test_booking_in_the_past(self):
        self.login()
        response = self.client.post('/booking', data={
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'service': self.service.name
        }, follow_redirects=True)
        self.assertIn('Nem lehet múltbeli dátumot választani.', response.data.decode('utf-8'))

    def test_booking_on_weekend(self):
        self.login()
        weekend = datetime.now() + timedelta(days=(5 - datetime.now().weekday()) % 7 + 1) 
        response = self.client.post('/booking', data={
            'date': weekend.strftime('%Y-%m-%d'),
            'time': '10:00',
            'service': self.service.name
        }, follow_redirects=True)
        self.assertIn('Hétvégére nem lehet foglalni.', response.data.decode('utf-8'))

    def test_blocked_time_conflict(self):
        self.login()
        day = datetime.now() + timedelta(days=1)
        booking = Booking(
            date=day.date(),
            time='10:00',
            service=self.service.name,
            user_id=self.user.id
        )
        db.session.add(booking)
        db.session.commit()

        response = self.client.post('/booking', data={
            'date': day.strftime('%Y-%m-%d'),
            'time': '10:30',
            'service': self.service.name
        }, follow_redirects=True)
        self.assertIn('Ez az időpont vagy annak közvetlen előtte/utána lévő félórája már foglalt.', response.data.decode('utf-8'))

    def test_edit_booking(self):
        self.login()
        booking = Booking(
            date=date.today(),
            time="10:00",
            service=self.service.name,
            user_id=self.user.id
        )
        db.session.add(booking)
        db.session.commit()

        new_date = date.today() + timedelta(days=1)

        response = self.client.post(f'/booking/edit/{booking.id}', data={
            'date': new_date.strftime('%Y-%m-%d'),
            'time': '11:00',
            'service': self.service.name
        }, follow_redirects=True)

        html = response.data.decode('utf-8')
        self.assertIn('Foglalás módosítva.', html)

        updated_booking = Booking.query.get(booking.id)
        self.assertEqual(updated_booking.time, '11:00')
        self.assertEqual(updated_booking.date, new_date)

    def test_delete_booking(self):
        self.login()
        booking = Booking(
            date=date.today(),
            time="12:00",
            service=self.service.name,
            user_id=self.user.id
        )
        db.session.add(booking)
        db.session.commit()

        response = self.client.get(f'/booking/delete/{booking.id}', follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Foglalás törölve.', html)

        deleted = Booking.query.get(booking.id)
        self.assertIsNone(deleted)

if __name__ == '__main__':
    unittest.main()
