import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import create_app, db
from app.models import User, Booking, MassageService
from flask import url_for
from datetime import datetime, date, time, timedelta

class BookingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.client = self.app.test_client()

        self.user = User(name="Teszt Elek", email="teszt@example.com", password="hashed", is_admin=False)
        db.session.add(self.user)

        self.service = MassageService(name="Svédmasszázs", description="Pihentető", price=10000)
        db.session.add(self.service)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_booking_creation(self):
        booking = Booking(
            date=date.today() + timedelta(days=1),
            time="10:00",
            service=self.service.name,
            user_id=self.user.id
        )
        db.session.add(booking)
        db.session.commit()

        self.assertEqual(Booking.query.count(), 1)
        saved = Booking.query.first()
        self.assertEqual(saved.time, "10:00")
        self.assertEqual(saved.service, self.service.name)

    def test_user_model(self):
        user = User.query.filter_by(email="teszt@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Teszt Elek")

    def test_service_model(self):
        service = MassageService.query.first()
        self.assertEqual(service.name, "Svédmasszázs")
        self.assertTrue(service.price > 0)

    def test_booking_time_format(self):
        booking = Booking(
            date=date.today() + timedelta(days=2),
            time="14:30",
            service=self.service.name,
            user_id=self.user.id
        )
        db.session.add(booking)
        db.session.commit()

        saved = Booking.query.first()
        self.assertRegex(saved.time, r'^\d{2}:\d{2}$')

    def test_multiple_bookings(self):
        for i in range(3):
            booking = Booking(
                date=date.today() + timedelta(days=i+1),
                time="09:00",
                service=self.service.name,
                user_id=self.user.id
            )
            db.session.add(booking)
        db.session.commit()

        self.assertEqual(Booking.query.count(), 3)

    def test_duplicate_user_email(self):
        duplicate = User(name="Másik Teszt", email="teszt@example.com", password="hashed")
        db.session.add(duplicate)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
