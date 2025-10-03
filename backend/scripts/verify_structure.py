#!/usr/bin/env python3
"""
Backend Structure Verification Script

Run this to verify all modules are properly exported and accessible.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_models():
    """Verify all models are properly exported"""
    print("\n🔍 Verifying Models...")
    try:
        from models import User, Inventory, ItemStatus, ConsumptionLog, RecipeHistory
        
        print("✅ User model imported")
        print("✅ Inventory model imported")
        print("✅ ItemStatus enum imported")
        print("✅ ConsumptionLog model imported")
        print("✅ RecipeHistory model imported")
        print("✅ All models properly exported!")
        return True
    except ImportError as e:
        print(f"❌ Model import error: {e}")
        return False


def verify_schemas():
    """Verify all schemas are properly exported"""
    print("\n🔍 Verifying Schemas...")
    try:
        from schemas import (
            UserCreate, UserResponse, UserUpdate,
            InventoryCreate, InventoryResponse, InventoryUpdate,
            InventoryMarkUsed, BulkInventoryCreate,
            RecipeIngredient, RecipeNutrition, RecipeData,
            RecipeSave, RecipeHistoryResponse
        )
        
        print("✅ User schemas imported")
        print("✅ Inventory schemas imported")
        print("✅ Recipe schemas imported")
        print("✅ All schemas properly exported!")
        return True
    except ImportError as e:
        print(f"❌ Schema import error: {e}")
        return False


def verify_crud():
    """Verify all CRUD functions are properly exported"""
    print("\n🔍 Verifying CRUD Functions...")
    try:
        from crud import (
            create_or_update_user, get_user, update_user,
            create_inventory_item, get_user_inventory, get_inventory_item,
            update_inventory_item, delete_inventory_item, mark_item_as_used,
            get_common_items,
            save_recipe, get_user_recipes, get_recipe_by_id,
            mark_recipe_cooked, toggle_favorite, delete_recipe
        )
        
        print("✅ User CRUD functions imported")
        print("✅ Inventory CRUD functions imported")
        print("✅ Recipe CRUD functions imported")
        print("✅ All CRUD functions properly exported!")
        return True
    except ImportError as e:
        print(f"❌ CRUD import error: {e}")
        return False


def verify_routers():
    """Verify all routers are properly exported"""
    print("\n🔍 Verifying Routers...")
    try:
        from routers import health, users, inventory, ai, recipes
        
        print("✅ Health router imported")
        print("✅ Users router imported")
        print("✅ Inventory router imported")
        print("✅ AI router imported")
        print("✅ Recipes router imported")
        print("✅ All routers properly exported!")
        return True
    except ImportError as e:
        print(f"❌ Router import error: {e}")
        return False


def verify_mark_as_used():
    """Verify mark as used functionality exists"""
    print("\n🔍 Verifying Mark As Used Functionality...")
    try:
        from crud.inventory import mark_item_as_used
        from schemas.inventory import InventoryMarkUsed
        
        # Check function signature
        import inspect
        sig = inspect.signature(mark_item_as_used)
        params = list(sig.parameters.keys())
        
        assert 'db' in params, "Missing 'db' parameter"
        assert 'item_id' in params, "Missing 'item_id' parameter"
        assert 'firebase_uid' in params, "Missing 'firebase_uid' parameter"
        assert 'used_data' in params, "Missing 'used_data' parameter"
        
        print("✅ mark_item_as_used function exists")
        print("✅ InventoryMarkUsed schema exists")
        print("✅ Function signature correct")
        print("✅ Mark as used feature properly implemented!")
        return True
    except (ImportError, AssertionError) as e:
        print(f"❌ Mark as used verification error: {e}")
        return False


def verify_recipe_endpoints():
    """Verify recipe endpoints exist"""
    print("\n🔍 Verifying Recipe Endpoints...")
    try:
        from routers.recipes import router
        
        # Check routes
        routes = [route.path for route in router.routes]
        
        assert '/save' in routes, "Missing /save endpoint"
        assert '/list' in routes, "Missing /list endpoint"
        assert '/{recipe_id}' in routes, "Missing /{recipe_id} endpoint"
        assert '/{recipe_id}/mark-cooked' in routes, "Missing /mark-cooked endpoint"
        assert '/{recipe_id}/toggle-favorite' in routes, "Missing /toggle-favorite endpoint"
        
        print("✅ /save endpoint exists")
        print("✅ /list endpoint exists")
        print("✅ /{recipe_id} endpoint exists")
        print("✅ /mark-cooked endpoint exists")
        print("✅ /toggle-favorite endpoint exists")
        print("✅ All recipe endpoints properly defined!")
        return True
    except (ImportError, AssertionError) as e:
        print(f"❌ Recipe endpoint verification error: {e}")
        return False


def main():
    """Run all verifications"""
    print("=" * 60)
    print("🚀 Backend Structure Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Models", verify_models()))
    results.append(("Schemas", verify_schemas()))
    results.append(("CRUD", verify_crud()))
    results.append(("Routers", verify_routers()))
    results.append(("Mark as Used", verify_mark_as_used()))
    results.append(("Recipe Endpoints", verify_recipe_endpoints()))
    
    print("\n" + "=" * 60)
    print("📊 Verification Results")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 All verifications passed! Backend structure is clean!")
        print("=" * 60)
        return 0
    else:
        print("⚠️  Some verifications failed. Check errors above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
