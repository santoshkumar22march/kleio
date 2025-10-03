
# Tests for inventory endpoints


import pytest
from unittest.mock import patch


@patch("utils.auth.verify_firebase_token")
def test_add_inventory_item(mock_verify, client, sample_inventory_data):
    """Test adding an inventory item"""
    mock_verify.return_value = "test_user_123"
    
    response = client.post(
        "/api/inventory/add",
        headers={"Authorization": "Bearer test_token"},
        json=sample_inventory_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["item_name"] == "Tomatoes"
    assert data["quantity"] == 2.0
    assert data["firebase_uid"] == "test_user_123"


@patch("utils.auth.verify_firebase_token")
def test_list_inventory(mock_verify, client, sample_inventory_data):
    """Test listing inventory items"""
    mock_verify.return_value = "test_user_123"
    
    # Add an item first
    client.post(
        "/api/inventory/add",
        headers={"Authorization": "Bearer test_token"},
        json=sample_inventory_data
    )
    
    # List items
    response = client.get(
        "/api/inventory/list",
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["item_name"] == "Tomatoes"


@patch("utils.auth.verify_firebase_token")
def test_user_can_only_see_own_items(mock_verify, client, sample_inventory_data):
    """Test that users can only see their own inventory"""
    # User 1 adds item
    mock_verify.return_value = "user_1"
    client.post(
        "/api/inventory/add",
        headers={"Authorization": "Bearer token1"},
        json=sample_inventory_data
    )
    
    # User 2 should not see User 1's items
    mock_verify.return_value = "user_2"
    response = client.get(
        "/api/inventory/list",
        headers={"Authorization": "Bearer token2"}
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 0  # Empty list for user 2


def test_get_categories():
    """Test getting categories list (public endpoint)"""
    response = client.get("/api/inventory/categories")
    assert response.status_code == 200
    categories = response.json()
    assert "vegetables" in categories
    assert "fruits" in categories


def test_get_units():
    """Test getting units list (public endpoint)"""
    response = client.get("/api/inventory/units")
    assert response.status_code == 200
    units = response.json()
    assert "kg" in units
    assert "liters" in units

