import json
import logging
import asyncio
from sqlalchemy.orm import Session

from crud.inventory import get_user_inventory
from models.inventory import ItemStatus
from utils.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

def check_recipe_feasibility(firebase_uid: str, db_session: Session, preferences: str = "") -> str:
    """
    Check if a recipe is feasible with current inventory items.
    """
    logger.info(f"🔧 TOOL: check_recipe_feasibility | Preferences: {preferences}")
    try:
        inventory_items = get_user_inventory(
            db_session,
            firebase_uid,
            status=ItemStatus.ACTIVE,
            limit=500
        )
        if not inventory_items:
            return json.dumps({
                "success": False,
                "error": "Empty inventory",
                "message": "No items in inventory to generate recipe"
            })
        available_items = [f"{item.item_name} ({item.quantity}{item.unit})" for item in inventory_items]
        filters = {"cooking_time": 45, "meal_type": "any", "cuisine": "Indian"}
        prefs_lower = preferences.lower()
        if "quick" in prefs_lower or "fast" in prefs_lower or "30" in prefs_lower:
            filters["cooking_time"] = 30
        if "lunch" in prefs_lower:
            filters["meal_type"] = "lunch"
        elif "dinner" in prefs_lower:
            filters["meal_type"] = "dinner"
        elif "breakfast" in prefs_lower:
            filters["meal_type"] = "breakfast"
        gemini = get_gemini_client()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        recipe = loop.run_until_complete(gemini.generate_recipe(
            available_items=available_items,
            dietary_preferences={
                "vegetarian": "vegetarian" in prefs_lower or "veg" in prefs_lower,
                "vegan": "vegan" in prefs_lower,
            },
            filters=filters
        ))
        result = {
            "success": True,
            "recipe_name": recipe.get("recipe_name"),
            "description": recipe.get("description"),
            "cooking_time": recipe.get("cooking_time_minutes"),
            "servings": recipe.get("servings"),
            "difficulty": recipe.get("difficulty"),
            "ingredients": recipe.get("ingredients", []),
            "available_count": sum(1 for ing in recipe.get("ingredients", []) if ing.get("available")),
            "missing_count": sum(1 for ing in recipe.get("ingredients", []) if not ing.get("available")),
            "feasible": sum(1 for ing in recipe.get("ingredients", []) if ing.get("available")) >= len(recipe.get("ingredients", [])) * 0.7
        }
        logger.info(f"🔧 RESULT: Recipe '{result['recipe_name']}' - {result['available_count']}/{len(recipe.get('ingredients', []))} items available")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return json.dumps({"error": str(e), "success": False})
