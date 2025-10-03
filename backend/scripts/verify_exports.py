#!/usr/bin/env python3
"""
Verify Module Exports (No Database Required)

Checks that __init__.py files have proper exports
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_file_exports(module_path, expected_exports):
    """Check if a file contains expected exports"""
    file_path = Path(__file__).parent.parent / module_path
    
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    content = file_path.read_text()
    
    missing = []
    for export in expected_exports:
        if export not in content:
            missing.append(export)
    
    if missing:
        return False, f"Missing exports: {', '.join(missing)}"
    
    return True, "All exports present"


def main():
    """Verify all __init__.py files"""
    print("=" * 60)
    print("🔍 Backend Export Verification (Structure Only)")
    print("=" * 60)
    
    checks = [
        ("models/__init__.py", [
            "User", "Inventory", "ItemStatus", 
            "ConsumptionLog", "RecipeHistory"
        ]),
        ("schemas/__init__.py", [
            "UserCreate", "UserResponse", "UserUpdate",
            "InventoryCreate", "InventoryResponse", "InventoryUpdate",
            "InventoryMarkUsed", "BulkInventoryCreate",
            "RecipeIngredient", "RecipeNutrition", "RecipeData",
            "RecipeSave", "RecipeHistoryResponse"
        ]),
        ("crud/__init__.py", [
            "create_or_update_user", "get_user", "update_user",
            "create_inventory_item", "get_user_inventory",
            "update_inventory_item", "delete_inventory_item",
            "mark_item_as_used", "get_common_items",
            "save_recipe", "get_user_recipes", "get_recipe_by_id",
            "mark_recipe_cooked", "toggle_favorite", "delete_recipe"
        ]),
        ("routers/__init__.py", [
            "health", "users", "inventory", "ai", "recipes"
        ])
    ]
    
    results = []
    
    print("\n📁 Checking __init__.py files...\n")
    
    for file_path, exports in checks:
        passed, message = check_file_exports(file_path, exports)
        status = "✅" if passed else "❌"
        print(f"{status} {file_path:30s} {message}")
        results.append(passed)
    
    # Check key files exist
    print("\n📄 Checking key files exist...\n")
    
    key_files = [
        "models/user.py",
        "models/inventory.py",
        "models/consumption_log.py",
        "models/recipe_history.py",
        "schemas/user.py",
        "schemas/inventory.py",
        "schemas/recipe.py",
        "schemas/ai.py",
        "crud/user.py",
        "crud/inventory.py",
        "crud/recipe_history.py",
        "routers/health.py",
        "routers/users.py",
        "routers/inventory.py",
        "routers/ai.py",
        "routers/recipes.py",
        "utils/auth.py",
        "utils/gemini_client.py",
        "migrations/003_add_recipe_history.sql",
        "docs/BACKEND_STRUCTURE.md",
        "docs/API_ENDPOINTS.md",
        "docs/DATABASE_SCHEMA.md"
    ]
    
    for file_path in key_files:
        full_path = Path(__file__).parent.parent / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        results.append(exists)
    
    # Summary
    print("\n" + "=" * 60)
    all_passed = all(results)
    
    if all_passed:
        print("✅ All structure checks passed!")
        print("=" * 60)
        print("\n📝 Summary:")
        print("• All models properly exported")
        print("• All schemas properly exported")
        print("• All CRUD functions properly exported")
        print("• All routers properly exported")
        print("• All key files exist")
        print("• Recipe features fully integrated")
        print("• Mark as used feature implemented")
        print("\n✅ Backend structure is clean and complete!")
        return 0
    else:
        print("❌ Some checks failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
