import json
import logging
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from schemas.inventory import InventoryCreate
from crud.inventory import create_inventory_item, get_user_inventory
from models.inventory import ItemStatus
from utils.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

def add_items_wrapper(items_text: str, firebase_uid: str, db_session: Session) -> str:
    """
    Add items to user's inventory from natural language input.
    """
    logger.info(f"🔧 TOOL: add_items_wrapper | Input: {items_text}")
    try:
        gemini = get_gemini_client()
        prompt = f'''
            Parse this natural language text into structured grocery items:
            "{items_text}"

            Return ONLY valid JSON array (no markdown):
            [
            {{"item_name": "tomatoes", "quantity": 2.0, "unit": "kg", "category": "vegetables"}},
            {{"item_name": "milk", "quantity": 1.0, "unit": "liter", "category": "dairy"}}
            ]

            Categories: vegetables, fruits, dairy, staples, pulses, spices, snacks, beverages, meat, seafood, bakery, frozen, oils, condiments, others'''
        response = gemini.client.models.generate_content(
            model=gemini.MODEL_ID,
            contents=prompt,
            config={"temperature": 0.3, "response_mime_type": "application/json"}
        )
        items_data = json.loads(response.text)
        if not isinstance(items_data, list) or not items_data:
            return json.dumps({"error": "Could not parse items", "items": []})
        added_items = []
        for item_dict in items_data:
            item = InventoryCreate(**item_dict)
            created_item = create_inventory_item(db_session, firebase_uid, item)
            added_items.append({
                "name": created_item.item_name,
                "quantity": float(created_item.quantity),
                "unit": created_item.unit,
                "category": created_item.category
            })
            logger.info(f"✅ DB: Added {created_item.item_name}")
        result = {"success": True, "items_added": added_items, "count": len(added_items)}
        logger.info(f"🔧 RESULT: {len(added_items)} items added")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return json.dumps({"error": str(e), "success": False})

def query_inventory_wrapper(firebase_uid: str, db_session: Session, category: Optional[str] = None) -> str:
    """
    Query user's current inventory items.
    """
    logger.info(f"🔧 TOOL: query_inventory_wrapper | Category: {category}")
    try:
        inventory_items = get_user_inventory(
            db_session,
            firebase_uid,
            status=ItemStatus.ACTIVE,
            category=category,
            limit=100
        )
        if not inventory_items:
            return json.dumps({
                "success": True,
                "items": [],
                "total": 0,
                "message": f"No {category} items found" if category else "Inventory is empty"
            })
        items_data = []
        for item in inventory_items:
            expiry_info = None
            if item.expiry_date:
                days_left = (item.expiry_date - date.today()).days
                expiry_info = {
                    "date": item.expiry_date.isoformat(),
                    "days_left": days_left,
                    "status": "urgent" if days_left <= 3 else "soon" if days_left <= 7 else "ok"
                }
            items_data.append({
                "name": item.item_name,
                "quantity": float(item.quantity),
                "unit": item.unit,
                "category": item.category,
                "expiry": expiry_info,
                "added_date": item.added_date.isoformat()
            })
        by_category = {}
        for item_data in items_data:
            cat = item_data["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item_data)
        result = {
            "success": True,
            "items": items_data,
            "by_category": by_category,
            "total": len(items_data)
        }
        logger.info(f"🔧 RESULT: {len(items_data)} items in inventory")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return json.dumps({"error": str(e), "success": False})
