import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from utils.pattern_analyzer import generate_shopping_list

logger = logging.getLogger(__name__)

def get_shopping_wrapper(firebase_uid: str, db_session: Session, urgency: Optional[str] = None) -> str:
    """
    Get smart shopping list based on usage patterns.
    """
    logger.info(f"🔧 TOOL: get_shopping_wrapper | Urgency: {urgency}")
    try:
        shopping_list = generate_shopping_list(
            db=db_session,
            firebase_uid=firebase_uid,
            urgency_filter=urgency
        )
        result = {
            "success": True,
            "urgent": shopping_list["urgent"],
            "this_week": shopping_list["this_week"],
            "later": shopping_list["later"],
            "total_items": len(shopping_list["urgent"]) + len(shopping_list["this_week"]) + len(shopping_list["later"])
        }
        logger.info(f"🔧 RESULT: {result['total_items']} items in shopping list")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return json.dumps({"error": str(e), "success": False})
