import os
import tempfile
import pytest
from app import create_app, db
from app.core.models import User, FinancialFile
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    UPLOAD_FOLDER = tempfile.mkdtemp()
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for the application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Test CLI runner for the application."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create test user."""
    user = User(username='test_user', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def auth_client(client, test_user):
    """Authenticated test client."""
    with client:
        client.post('/auth/login', data={
            'username': 'test_user',
            'password': 'password'
        }, follow_redirects=True)
        yield client

@pytest.fixture
def test_file(app, test_user):
    """Create test financial file."""
    file = FinancialFile(
        filename='test.csv',
        file_type='csv',
        user_id=test_user.id
    )
    db.session.add(file)
    db.session.commit()
    return file
