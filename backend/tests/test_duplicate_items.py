"""
Test for duplicate item handling
Ensures items with same name update quantity instead of creating duplicates
"""

import pytest
from unittest.mock import patch


@patch("utils.auth.verify_firebase_token")
def test_adding_same_item_updates_quantity(mock_verify, client):
    """Test that adding the same item twice updates quantity instead of duplicating"""
    mock_verify.return_value = "test_user_123"
    headers = {"Authorization": "Bearer test_token"}
    
    # Add tomatoes - 2kg
    response1 = client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 2.0,
            "unit": "kg"
        }
    )
    
    assert response1.status_code == 201
    item1 = response1.json()
    item1_id = item1["id"]
    assert item1["quantity"] == 2.0
    
    # Add tomatoes again - 1kg more
    response2 = client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",  # Same name
            "category": "vegetables",
            "quantity": 1.0,
            "unit": "kg"
        }
    )
    
    assert response2.status_code == 201
    item2 = response2.json()
    
    # Should return the SAME item with UPDATED quantity
    assert item2["id"] == item1_id  # Same ID
    assert item2["quantity"] == 3.0  # 2 + 1 = 3kg
    
    # List inventory - should only have ONE tomatoes entry
    response3 = client.get("/api/inventory/list", headers=headers)
    items = response3.json()
    
    tomatoes = [item for item in items if item["item_name"].lower() == "tomatoes"]
    assert len(tomatoes) == 1  # Only one entry
    assert tomatoes[0]["quantity"] == 3.0


@patch("utils.auth.verify_firebase_token")
def test_case_insensitive_matching(mock_verify, client):
    """Test that item names are matched case-insensitively"""
    mock_verify.return_value = "test_user_123"
    headers = {"Authorization": "Bearer test_token"}
    
    # Add "Tomatoes"
    response1 = client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 2.0,
            "unit": "kg"
        }
    )
    assert response1.status_code == 201
    item1_id = response1.json()["id"]
    
    # Add "tomatoes" (lowercase)
    response2 = client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "tomatoes",  # Different case
            "category": "vegetables",
            "quantity": 1.0,
            "unit": "kg"
        }
    )
    
    assert response2.status_code == 201
    item2 = response2.json()
    
    # Should update the same item
    assert item2["id"] == item1_id
    assert item2["quantity"] == 3.0


@patch("utils.auth.verify_firebase_token")
def test_consumed_items_dont_get_updated(mock_verify, client):
    """Test that consumed items are not updated, a new entry is created instead"""
    mock_verify.return_value = "test_user_123"
    headers = {"Authorization": "Bearer test_token"}
    
    # Add tomatoes
    response1 = client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 2.0,
            "unit": "kg"
        }
    )
    item1_id = response1.json()["id"]
    
    # Mark as consumed
    client.post(f"/api/inventory/{item1_id}/mark-used", headers=headers, json={})
    
    # Add tomatoes again (after consuming)
    response2 = client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 1.0,
            "unit": "kg"
        }
    )
    
    item2 = response2.json()
    
    # Should create a NEW item (not update consumed one)
    assert item2["id"] != item1_id
    assert item2["quantity"] == 1.0
    assert item2["status"] == "active"


@patch("utils.auth.verify_firebase_token")
def test_bulk_add_with_duplicates(mock_verify, client):
    """Test bulk add with items that already exist"""
    mock_verify.return_value = "test_user_123"
    headers = {"Authorization": "Bearer test_token"}
    
    # Add initial inventory
    client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 2.0,
            "unit": "kg"
        }
    )
    
    # Bulk add including tomatoes
    response = client.post(
        "/api/inventory/bulk-add",
        headers=headers,
        json={
            "items": [
                {
                    "item_name": "Tomatoes",  # Already exists
                    "category": "vegetables",
                    "quantity": 1.0,
                    "unit": "kg"
                },
                {
                    "item_name": "Onions",  # New item
                    "category": "vegetables",
                    "quantity": 1.5,
                    "unit": "kg"
                }
            ]
        }
    )
    
    assert response.status_code == 201
    items = response.json()
    
    # Check results
    response = client.get("/api/inventory/list", headers=headers)
    inventory = response.json()
    
    tomatoes = [i for i in inventory if i["item_name"].lower() == "tomatoes"]
    onions = [i for i in inventory if i["item_name"].lower() == "onions"]
    
    assert len(tomatoes) == 1  # Only one entry
    assert tomatoes[0]["quantity"] == 3.0  # 2 + 1
    
    assert len(onions) == 1
    assert onions[0]["quantity"] == 1.5


@patch("utils.auth.verify_firebase_token")
def test_different_items_create_separate_entries(mock_verify, client):
    """Test that different items create separate entries (not merged)"""
    mock_verify.return_value = "test_user_123"
    headers = {"Authorization": "Bearer test_token"}
    
    # Add tomatoes
    client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 2.0,
            "unit": "kg"
        }
    )
    
    # Add onions
    client.post(
        "/api/inventory/add",
        headers=headers,
        json={
            "item_name": "Onions",
            "category": "vegetables",
            "quantity": 1.0,
            "unit": "kg"
        }
    )
    
    # List inventory
    response = client.get("/api/inventory/list", headers=headers)
    items = response.json()
    
    assert len(items) == 2  # Two separate items
    assert any(i["item_name"].lower() == "tomatoes" for i in items)
    assert any(i["item_name"].lower() == "onions" for i in items)

