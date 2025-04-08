import sys
import os
import unittest
import tempfile
from werkzeug.security import generate_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, MassageService

class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        self.admin = User(name='Admin', email='admin@test.com', password=generate_password_hash('admin123'), is_admin=True)
        self.user = User(name='Felhasználó', email='user@test.com', password=generate_password_hash('user123'))
        db.session.add_all([self.admin, self.user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as_admin(self):
        self.client.post('/login', data={'email': 'admin@test.com', 'password': 'admin123'}, follow_redirects=True)

    def test_admin_access(self):
        self.login_as_admin()
        response = self.client.get('/admin')
        html = response.data.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Zentime Masszázs Stúdó', html)

    def test_user_deletion(self):
        self.login_as_admin()
        response = self.client.get(f'/admin/delete_user/{self.user.id}', follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Felhasználó törölve.', html)
        self.assertIsNone(User.query.get(self.user.id))

    def test_add_service(self):
        self.login_as_admin()
        response = self.client.post('/admin/add_service', data={
            'name': 'Teszt Szolgáltatás',
            'description': 'Ez egy leírás.',
            'price': 12000,
            'image': (tempfile.NamedTemporaryFile(suffix='.jpg'), 'test.jpg')
        }, content_type='multipart/form-data', follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Szolgáltatás hozzáadva.', html)
        self.assertIsNotNone(MassageService.query.filter_by(name='Teszt Szolgáltatás').first())

    def test_delete_service(self):
        self.login_as_admin()
        service = MassageService(name='Törlendő', description='...', price=5000)
        db.session.add(service)
        db.session.commit()
        response = self.client.get(f'/admin/delete_service/{service.id}', follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Szolgáltatás törölve.', html)
        self.assertIsNone(MassageService.query.get(service.id))

    def test_edit_service(self):
        self.login_as_admin()
        service = MassageService(name='Eredeti', description='Leírás', price=9000)
        db.session.add(service)
        db.session.commit()

        response = self.client.post(f'/admin/edit_service/{service.id}', data={
            'name': 'Módosított',
            'description': 'Módosított leírás',
            'price': 15000
        }, follow_redirects=True)
        html = response.data.decode('utf-8')
        self.assertIn('Szolgáltatás frissítve.', html)
        updated = MassageService.query.get(service.id)
        self.assertEqual(updated.name, 'Módosított')
        self.assertEqual(updated.description, 'Módosított leírás')
        self.assertEqual(updated.price, 15000)

if __name__ == '__main__':
    unittest.main()
