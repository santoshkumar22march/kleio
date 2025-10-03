"""
Tests for Firebase authentication

Note: These tests mock Firebase verification
For integration tests with real Firebase, use a test Firebase project
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from firebase_admin import auth

from main import app

client = TestClient(app)


def test_health_check_no_auth():
    """Health check should work without authentication"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_protected_endpoint_without_token():
    """Protected endpoints should reject requests without token"""
    response = client.get("/api/users/profile")
    assert response.status_code == 403  # No Authorization header


def test_protected_endpoint_with_invalid_token():
    """Protected endpoints should reject invalid tokens"""
    response = client.get(
        "/api/users/profile",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


@patch("utils.auth.auth.verify_id_token")
def test_protected_endpoint_with_valid_token(mock_verify):
    """Protected endpoints should accept valid Firebase tokens"""
    # Mock Firebase token verification
    mock_verify.return_value = {"uid": "test_user_123"}
    
    response = client.get(
        "/api/users/profile",
        headers={"Authorization": "Bearer valid_test_token"}
    )
    
    # Should reach endpoint (might return 404 if user doesn't exist, but auth passed)
    assert response.status_code in [200, 404]  # Auth successful


@patch("utils.auth.auth.verify_id_token")
def test_get_current_user(mock_verify):
    """Test that firebase_uid is correctly extracted from token"""
    mock_verify.return_value = {"uid": "test_user_456"}
    
    response = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer valid_token"}
    )
    
    assert response.status_code == 200
    assert response.json()["firebase_uid"] == "test_user_456"


def test_no_fallback_authentication():
    """Ensure there are no alternative authentication methods"""
    # All protected endpoints must require Firebase token
    protected_endpoints = [
        "/api/users/profile",
        "/api/inventory/list",
        "/api/inventory/add",
    ]
    
    for endpoint in protected_endpoints:
        # No token
        response = client.get(endpoint)
        assert response.status_code in [403, 405]  # Forbidden or Method Not Allowed
        
        # Invalid token
        response = client.get(
            endpoint,
            headers={"Authorization": "Bearer fake_token"}
        )
        assert response.status_code == 401  # Unauthorized

