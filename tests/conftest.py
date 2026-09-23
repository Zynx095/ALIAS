"""ALIAS Test Configuration and Fixtures."""
import pytest
import sys
import os

# Add backend/app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

# Set test environment variables before importing app modules
os.environ['DATABASE_URL'] = 'sqlite:///./test_alias.db'
os.environ['ENVIRONMENT'] = 'testing'
os.environ['JWT_SECRET'] = 'test-secret-key'

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, get_db
from main import app

# Test database setup
TEST_DATABASE_URL = 'sqlite:///./test_alias.db'
test_engine = create_engine(TEST_DATABASE_URL, connect_args={'check_same_thread': False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    """Create test database tables before tests, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    # Clean up test database file
    if os.path.exists('./test_alias.db'):
        try:
            os.remove('./test_alias.db')
        except OSError:
            pass


@pytest.fixture(scope='function')
def db_session():
    """Provide a clean database session for each test."""
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope='module')
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_login_event():
    """Sample valid login event data."""
    return {
        'user_id': 'test.user@acme.corp',
        'ip_address': '203.0.113.42',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'location': 'Bengaluru, India',
        'device_fingerprint': 'win11-chrome-abc123',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'auth_status': 'SUCCESS',
        'failed_attempts': 0,
        'access_pattern': 'DIRECT'
    }
