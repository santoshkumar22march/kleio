"""
Test AI features: Receipt parsing and recipe generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import requests
from PIL import Image, ImageDraw, ImageFont
import io


def create_test_receipt():
    """Create a sample receipt image for testing"""
    
    # Create a simple receipt image
    width, height = 400, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw receipt content
    y = 20
    
    # Header
    draw.text((width//2 - 80, y), "FRESH MART", fill='black', font=font)
    y += 40
    draw.text((10, y), "Receipt #12345", fill='black', font=font_small)
    y += 30
    draw.line([(10, y), (width-10, y)], fill='black', width=2)
    y += 20
    
    # Items
    items = [
        ("Tomatoes", "2.0 kg", "₹80.00"),
        ("Onions", "1.5 kg", "₹60.00"),
        ("Toor Dal", "1.0 kg", "₹120.00"),
        ("Rice (Basmati)", "5.0 kg", "₹400.00"),
        ("Milk", "2.0 L", "₹100.00"),
        ("Paneer", "250 g", "₹125.00"),
        ("Wheat Flour", "10.0 kg", "₹350.00"),
    ]
    
    for name, qty, price in items:
        draw.text((10, y), name, fill='black', font=font_small)
        draw.text((200, y), qty, fill='black', font=font_small)
        draw.text((300, y), price, fill='black', font=font_small)
        y += 30
    
    # Footer
    y += 20
    draw.line([(10, y), (width-10, y)], fill='black', width=2)
    y += 20
    draw.text((10, y), "TOTAL:", fill='black', font=font)
    draw.text((300, y), "₹1235.00", fill='black', font=font)
    y += 40
    draw.text((width//2 - 100, y), "Thank You! Come Again", fill='black', font=font_small)
    
    return img


async def test_receipt_parsing(token: str, base_url: str = "http://localhost:8000"):
    """Test receipt parsing endpoint"""
    
    print("\n" + "="*60)
    print("🧪 Testing Receipt Parsing")
    print("="*60)
    
    # Create test receipt
    print("\n1. Creating test receipt image...")
    receipt_img = create_test_receipt()
    
    # Save for reference
    receipt_path = Path(__file__).parent.parent / "test_receipt.jpg"
    receipt_img.save(receipt_path, "JPEG")
    print(f"   ✅ Test receipt saved to: {receipt_path}")
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    receipt_img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Test parse-receipt endpoint
    print("\n2. Sending receipt to AI for parsing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("receipt.jpg", img_byte_arr, "image/jpeg")}
    
    response = requests.post(
        f"{base_url}/api/ai/parse-receipt",
        headers=headers,
        files=files
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: {data['message']}")
        print(f"   📦 Items detected: {data['items_detected']}")
        
        if data['items']:
            print("\n   Detected Items:")
            for item in data['items']:
                conf = item['confidence'] * 100
                print(f"      • {item['name']}: {item['quantity']} {item['unit']} "
                      f"({item['category']}) - {conf:.0f}% confidence")
            
            # Test confirm endpoint
            print("\n3. Confirming and adding items to inventory...")
            
            inventory_items = [
                {
                    "item_name": item['name'].title(),
                    "category": item['category'],
                    "quantity": item['quantity'],
                    "unit": item['unit']
                }
                for item in data['items']
            ]
            
            response = requests.post(
                f"{base_url}/api/ai/confirm-receipt-items",
                headers=headers,
                json={"items": inventory_items}
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Failed to add items: {response.json()}")
    else:
        print(f"   ❌ Failed: {response.json()}")
    
    return response.status_code == 200


async def test_recipe_generation(token: str, base_url: str = "http://localhost:8000"):
    """Test recipe generation endpoint"""
    
    print("\n" + "="*60)
    print("🧪 Testing Recipe Generation")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, check inventory
    print("\n1. Checking inventory...")
    response = requests.get(
        f"{base_url}/api/ai/inventory-summary",
        headers=headers
    )
    
    if response.status_code == 200:
        summary = response.json()
        print(f"   ✅ {summary['summary']}")
        print(f"   Categories: {', '.join(summary['categories'].keys())}")
    else:
        print("   ⚠️  No inventory found. Add some items first.")
        return False
    
    # Generate recipe
    print("\n2. Generating recipe with AI...")
    
    recipe_request = {
        "cooking_time": 30,
        "meal_type": "dinner",
        "cuisine": "North Indian"
    }
    
    response = requests.post(
        f"{base_url}/api/ai/generate-recipe",
        headers=headers,
        json=recipe_request
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        recipe = response.json()
        
        print(f"\n   ✅ Recipe Generated!\n")
        print(f"   📖 {recipe['recipe_name']}")
        print(f"   📝 {recipe['description']}")
        print(f"   ⏱️  {recipe['cooking_time_minutes']} minutes")
        print(f"   👥 Serves {recipe['servings']}")
        print(f"   🍽️  {recipe['cuisine']} cuisine")
        print(f"   📊 Difficulty: {recipe['difficulty']}")
        
        print(f"\n   🥘 Ingredients:")
        for ing in recipe['ingredients']:
            status = "✓ Have" if ing['available'] else "✗ Need to buy"
            print(f"      • {ing['item']}: {ing['quantity']} {ing['unit']} - {status}")
        
        print(f"\n   📋 Instructions:")
        for i, step in enumerate(recipe['instructions'], 1):
            print(f"      {i}. {step}")
        
        if recipe.get('tips'):
            print(f"\n   💡 Tips:")
            for tip in recipe['tips']:
                print(f"      • {tip}")
        
        print(f"\n   📊 Nutrition (per serving):")
        nutrition = recipe['nutrition']
        print(f"      Calories: {nutrition['calories']} kcal")
        print(f"      Protein: {nutrition['protein']}g | Carbs: {nutrition['carbs']}g | "
              f"Fat: {nutrition['fat']}g | Fiber: {nutrition['fiber']}g")
        
        return True
    else:
        print(f"   ❌ Failed: {response.json()}")
        return False


async def main():
    """Run all AI feature tests"""
    
    print("="*60)
    print("🤖 Kleio.ai - AI Features Testing")
    print("="*60)
    
    # Get token
    token_file = Path(__file__).parent.parent / ".firebase_token"
    
    if not token_file.exists():
        print("\n❌ Firebase token not found!")
        print("   Run: python scripts/get_firebase_token.py")
        return 1
    
    token = token_file.read_text().strip()
    print(f"\n✅ Using token from {token_file}")
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("\n❌ Backend not responding!")
            print("   Start backend: uvicorn main:app --reload")
            return 1
        print("✅ Backend is running")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend!")
        print("   Start backend: uvicorn main:app --reload")
        return 1
    
    # Run tests
    receipt_ok = await test_receipt_parsing(token)
    recipe_ok = await test_recipe_generation(token)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Receipt Parsing: {'✅ PASS' if receipt_ok else '❌ FAIL'}")
    print(f"Recipe Generation: {'✅ PASS' if recipe_ok else '❌ FAIL'}")
    print("="*60)
    
    return 0 if (receipt_ok and recipe_ok) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

