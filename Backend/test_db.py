import pytest
from app import app
from database import db
from models import Role, FAQ

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()    # Clear any seeded tables first
            db.create_all()  # Create fresh empty tables for testing
            yield client

def test_role_creation(client):
    role = Role(role_name="Parent")
    db.session.add(role)
    db.session.commit()
    assert Role.query.count() == 1
    assert Role.query.first().role_name == "Parent"

def test_faq_creation(client):
    faq = FAQ(question="Test Q?", answer="Test A", category="Test")
    db.session.add(faq)
    db.session.commit()
    assert FAQ.query.count() == 1
    assert FAQ.query.first().category == "Test"