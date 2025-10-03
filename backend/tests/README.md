# Testing Guide

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run and show print statements
pytest -s
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Fixtures and configuration
├── test_auth.py          # Authentication tests
├── test_inventory.py     # Inventory endpoint tests
└── test_users.py         # User endpoint tests (add later)
```

## Fixtures Available

### `db`
Fresh database for each test
```python
def test_something(db):
    user = User(firebase_uid="test")
    db.add(user)
    db.commit()
```

### `client`
FastAPI TestClient
```python
def test_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
```

### `authenticated_client`
Client with mocked Firebase auth
```python
def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/api/users/profile")
    # Auth is automatically handled
```

### `mock_firebase_uid`
Returns test Firebase UID: "test_user_12345"

### `sample_user_data`
Sample user profile data

### `sample_inventory_data`
Sample inventory item data

## Testing Authentication

### Unit Tests (Mock Firebase)
```python
@patch("utils.auth.verify_firebase_token")
def test_something(mock_verify, client):
    mock_verify.return_value = "test_user_123"
    response = client.get(
        "/api/users/profile",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
```

### Integration Tests (Real Firebase)
For integration tests, create a Firebase test project:

1. Create test Firebase project
2. Get test credentials
3. Create test user
4. Get real ID token

```python
# integration_test.py (not run in CI)
from firebase_admin import auth

def test_with_real_firebase():
    # Get real token from test Firebase project
    token = get_test_firebase_token()
    
    response = client.get(
        "/api/users/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## Best Practices

1. **Mock Firebase in unit tests** - Fast and reliable
2. **Use fixtures** - DRY principle
3. **Test authentication** - Ensure all protected endpoints require tokens
4. **Test authorization** - Users can only access their own data
5. **Clean database** - Each test gets fresh database
6. **Test edge cases** - Invalid input, missing data, etc.

## Example Test

```python
@patch("utils.auth.verify_firebase_token")
def test_add_and_list_inventory(mock_verify, client):
    """Test full flow: add item then list"""
    # Mock Firebase auth
    mock_verify.return_value = "user_123"
    
    # Add item
    response = client.post(
        "/api/inventory/add",
        headers={"Authorization": "Bearer token"},
        json={
            "item_name": "Tomatoes",
            "category": "vegetables",
            "quantity": 2.0,
            "unit": "kg"
        }
    )
    assert response.status_code == 201
    
    # List items
    response = client.get(
        "/api/inventory/list",
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
```

## CI/CD

Add to GitHub Actions:
```yaml
- name: Run tests
  run: |
    cd backend
    pip install pytest pytest-cov
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

