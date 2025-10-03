# Pytest configuration and fixtures for testing

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from database import Base, get_db
from main import app

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create fresh database for each test

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    # Create test client with database override

    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_firebase_uid():
    # Mock Firebase UID for testing

    return "test_user_12345"


@pytest.fixture
def mock_firebase_token():
    # Mock Firebase token verification

    def mock_verify_token(credentials):
        return "test_user_12345"
    
    with patch("utils.auth.verify_firebase_token", side_effect=mock_verify_token):
        yield


@pytest.fixture
def authenticated_client(client, mock_firebase_token):
    # Test client with mocked Firebase authentication

    """
    Test client with mocked Firebase authentication
    
    Usage:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get("/api/users/profile")
            assert response.status_code == 200
    """
    return client


@pytest.fixture
def sample_user_data():
    # Sample user profile data

    return {
        "household_size": 4,
        "location_city": "Chennai",
        "language_preference": "ta",
        "dietary_preferences": {
            "vegetarian": True,
            "vegan": False,
            "diabetic": False
        },
        "region": "south"
    }


@pytest.fixture
def sample_inventory_data():
    # Sample inventory item data

    return {
        "item_name": "Tomatoes",
        "category": "vegetables",
        "quantity": 2.0,
        "unit": "kg"
    }

