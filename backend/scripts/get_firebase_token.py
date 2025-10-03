# Firebase Token Generator
# Get Firebase ID token for testing protected endpoints without frontend


import requests
import json
import os
from pathlib import Path
import sys

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


def get_firebase_token(email: str, password: str) -> str:
    """
    Get Firebase ID token using email/password
    
    Args:
        email: Test user email
        password: Test user password
        
    Returns:
        Firebase ID token (valid for 1 hour)
    """
    
    # Get Firebase Web API Key from environment
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    
    if not api_key:
        raise ValueError(
            "\n❌ FIREBASE_WEB_API_KEY not found in .env\n\n"
            "Get it from Firebase Console:\n"
            "1. Go to https://console.firebase.google.com\n"
            "2. Select your project\n"
            "3. Project Settings → General\n"
            "4. Copy 'Web API Key'\n"
            "5. Add to .env: FIREBASE_WEB_API_KEY=AIza...\n"
        )
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    print(f"🔄 Requesting token from Firebase...")
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        error_data = response.json()
        error_message = error_data.get("error", {}).get("message", "Unknown error")
        
        if "EMAIL_NOT_FOUND" in error_message:
            raise Exception(
                f"\n❌ User not found: {email}\n\n"
                f"Create test user in Firebase Console:\n"
                f"1. Go to https://console.firebase.google.com\n"
                f"2. Authentication → Users → Add user\n"
                f"3. Use email: {email}\n"
            )
        elif "INVALID_PASSWORD" in error_message:
            raise Exception(f"❌ Invalid password for {email}")
        else:
            raise Exception(f"❌ Firebase error: {error_message}")
    
    data = response.json()
    return data["idToken"], data.get("localId")


def test_endpoints(token: str, base_url: str = "http://localhost:8000"):
    """Test protected endpoints with token"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🧪 Testing endpoints at {base_url}\n")
    
    # Test health check (no auth needed)
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {base_url}")
        print(f"   Make sure backend is running: uvicorn main:app --reload")
        return False
    
    # Test protected endpoint
    response = requests.get(f"{base_url}/api/users/profile", headers=headers)
    print(f"✅ User profile: {response.status_code}", end="")
    
    if response.status_code == 404:
        print(" (not found - will create)")
        
        # Create user profile
        profile_data = {
            "household_size": 4,
            "location_city": "Test City",
            "language_preference": "en",
            "dietary_preferences": {"vegetarian": False},
            "region": "all"
        }
        
        response = requests.post(
            f"{base_url}/api/users/profile",
            headers=headers,
            json=profile_data
        )
        print(f"   ✅ Created profile: {response.status_code}")
    elif response.status_code == 200:
        print(" (found)")
    else:
        print(f"\n   ❌ Error: {response.json()}")
    
    # Test inventory endpoints
    response = requests.get(f"{base_url}/api/inventory/list", headers=headers)
    items_count = len(response.json()) if response.status_code == 200 else 0
    print(f"✅ Inventory list: {response.status_code} - {items_count} items")
    
    # Add a test item
    item_data = {
        "item_name": "Test Tomatoes",
        "category": "vegetables",
        "quantity": 2.5,
        "unit": "kg"
    }
    
    response = requests.post(
        f"{base_url}/api/inventory/add",
        headers=headers,
        json=item_data
    )
    
    if response.status_code == 201:
        print(f"✅ Add item: {response.status_code} - Test item added")
    else:
        print(f"❌ Add item: {response.status_code}")
        print(f"   Error: {response.json()}")
    
    print(f"\n✅ All endpoint tests complete!\n")
    return True


def main():
    print("=" * 60)
    print("🔐 Firebase Token Generator for Kleio.ai")
    print("=" * 60)
    
    # Get credentials
    print("\nEnter test user credentials:")
    email = input("  Email (default: test@kleio-ai.com): ").strip()
    if not email:
        email = "test@kleio-ai.com"
    
    password = input("  Password: ").strip()
    if not password:
        print("\n❌ Password required")
        return 1
    
    print(f"\n📧 Using email: {email}")
    
    try:
        # Get token
        token, user_id = get_firebase_token(email, password)
        
        print(f"✅ Token obtained successfully!")
        print(f"👤 User ID: {user_id}\n")
        
        # Display token
        print("=" * 60)
        print("🔑 Your Firebase Token (valid for 1 hour):")
        print("=" * 60)
        print(f"\n{token}\n")
        print("=" * 60)
        
        # Save to file
        token_file = Path(__file__).parent.parent / ".firebase_token"
        with open(token_file, "w") as f:
            f.write(token)
        print(f"\n💾 Token saved to: {token_file}")
        
        # Export command
        print(f"\n📋 To use in terminal:")
        print(f"   export TOKEN=\"{token}\"")
        print(f"   # Or on Windows PowerShell:")
        print(f"   $env:TOKEN=\"{token}\"")
        
        # Test endpoints
        print("\n" + "=" * 60)
        test = input("🧪 Test endpoints now? (y/n, default: y): ").strip().lower()
        
        if test != 'n':
            success = test_endpoints(token)
            if not success:
                return 1
        
        print("\n" + "=" * 60)
        print("✅ Done! Use the token above in your API requests.")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

