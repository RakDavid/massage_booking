import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app import create_app, db
from app.models import MassageService

class ServiceModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.service = MassageService(name="Talpmasszázs", description="Frissítő kezelés", price=8000)
        db.session.add(self.service)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_service_creation(self):
        service = MassageService.query.filter_by(name="Talpmasszázs").first()
        self.assertIsNotNone(service)
        self.assertEqual(service.description, "Frissítő kezelés")
        self.assertEqual(service.price, 8000)

    def test_service_price_positive(self):
        self.assertGreater(self.service.price, 0)

if __name__ == '__main__':
    unittest.main()
