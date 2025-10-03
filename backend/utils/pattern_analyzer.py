# Pattern analysis utility for usage pattern recognition
# Implements the smart algorithm to predict shopping needs

from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import date, timedelta
from statistics import mean, median
import logging

from models.inventory import Inventory, ItemStatus
from models.shopping_prediction import ShoppingPrediction, ConfidenceLevel, UrgencyLevel
from crud.purchase_log import get_item_purchase_pattern
from models.consumption_log import ConsumptionLog

logger = logging.getLogger(__name__)


# Category-specific buffer days (buy X days before running out)
CATEGORY_BUFFERS = {
    "vegetables": 1,    # Fresh items, buy quickly
    "fruits": 1,
    "dairy": 2,
    "meat": 2,
    "seafood": 1,
    "bakery": 1,
    "staples": 3,       # Rice, atta - long-lasting
    "pulses": 3,
    "oils": 5,
    "condiments": 5,
    "spices": 7,
    "snacks": 2,
    "beverages": 3,
    "frozen": 3,
    "default": 2
}


def get_category_buffer_days(category: str) -> int:
    """Get buffer days for a category (how many days before depletion to alert)"""
    return CATEGORY_BUFFERS.get(category.lower(), CATEGORY_BUFFERS["default"])


def calculate_confidence_level(data_points: int) -> ConfidenceLevel:
    """
    Calculate confidence level based on number of data points
    
    Args:
        data_points: Number of historical records
        
    Returns:
        ConfidenceLevel: LOW (<3), MEDIUM (3-4), HIGH (5+)
    """
    if data_points < 3:
        return ConfidenceLevel.LOW
    elif data_points < 5:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.HIGH


def calculate_urgency(
    days_until_depletion: float,
    category: str,
    current_stock: float
) -> UrgencyLevel:
    """
    Calculate urgency level based on predicted depletion time and category
    
    Args:
        days_until_depletion: Days until item runs out
        category: Item category
        current_stock: Current quantity in inventory
        
    Returns:
        UrgencyLevel: URGENT, THIS_WEEK, or LATER
    """
    buffer_days = get_category_buffer_days(category)
    
    # If no stock, it's urgent
    if current_stock <= 0:
        return UrgencyLevel.URGENT
    
    # Calculate urgency based on buffer
    if days_until_depletion <= buffer_days:
        return UrgencyLevel.URGENT
    elif days_until_depletion <= 7:
        return UrgencyLevel.THIS_WEEK
    else:
        return UrgencyLevel.LATER


def analyze_item_pattern(
    db: Session,
    firebase_uid: str,
    item_name: str,
    category: str
) -> Optional[Dict]:
    """
    Analyze consumption and purchase patterns for a specific item
    
    This is the CORE ALGORITHM that makes Kleio smart!
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        item_name: Name of item to analyze
        category: Item category
        
    Returns:
        dict | None: Pattern analysis result or None if insufficient data
    """
    
    # Step 1: Get purchase pattern
    purchase_pattern = get_item_purchase_pattern(
        db=db,
        firebase_uid=firebase_uid,
        item_name=item_name,
        min_records=2,  # Need at least 2 purchases
        max_records=10
    )
    
    if not purchase_pattern:
        logger.debug(f"No purchase pattern for {item_name}")
        return None
    
    # Step 2: Get consumption pattern
    consumption_logs = db.query(ConsumptionLog).filter(
        ConsumptionLog.firebase_uid == firebase_uid,
        ConsumptionLog.item_name.ilike(item_name)
    ).order_by(ConsumptionLog.consumed_date.desc()).limit(10).all()
    
    # Step 3: Get current stock
    current_item = db.query(Inventory).filter(
        Inventory.firebase_uid == firebase_uid,
        Inventory.item_name.ilike(item_name),
        Inventory.status == ItemStatus.ACTIVE
    ).first()
    
    current_stock = float(current_item.quantity) if current_item else 0.0
    unit = current_item.unit if current_item else "units"
    
    # Step 4: Calculate consumption rate
    avg_consumption_rate = None
    avg_days_lasted = None
    
    if consumption_logs:
        # Average days item lasts
        days_lasted_values = [log.days_lasted for log in consumption_logs if log.days_lasted > 0]
        if days_lasted_values:
            avg_days_lasted = mean(days_lasted_values)
            
            # Average quantity consumed per cycle
            quantities = [float(log.quantity_consumed) for log in consumption_logs]
            avg_quantity_consumed = mean(quantities)
            
            # Consumption rate = quantity per day
            avg_consumption_rate = avg_quantity_consumed / avg_days_lasted if avg_days_lasted > 0 else None
    
    # Step 5: Predict depletion date
    predicted_depletion_date = None
    days_until_depletion = 999  # Default large value
    
    if current_stock > 0 and avg_consumption_rate and avg_consumption_rate > 0:
        # We have stock and know consumption rate
        days_until_depletion = current_stock / avg_consumption_rate
        predicted_depletion_date = date.today() + timedelta(days=int(days_until_depletion))
    elif current_stock <= 0 and purchase_pattern["avg_days_between_purchases"]:
        # No stock, predict based on purchase frequency
        days_since_last = (date.today() - purchase_pattern["last_purchase_date"]).days
        if days_since_last >= purchase_pattern["avg_days_between_purchases"]:
            # Already overdue
            predicted_depletion_date = date.today()
            days_until_depletion = 0
        else:
            # Predict next purchase based on pattern
            predicted_depletion_date = purchase_pattern["last_purchase_date"] + timedelta(
                days=int(purchase_pattern["avg_days_between_purchases"])
            )
            days_until_depletion = (predicted_depletion_date - date.today()).days
    
    # Step 6: Calculate confidence
    total_data_points = purchase_pattern["purchase_count"] + len(consumption_logs)
    confidence = calculate_confidence_level(total_data_points)
    
    # Step 7: Calculate urgency
    urgency = calculate_urgency(days_until_depletion, category, current_stock)
    
    # Step 8: Suggest purchase quantity (average of past purchases)
    suggested_quantity = purchase_pattern["avg_quantity_per_purchase"]
    
    return {
        "item_name": item_name,
        "category": category,
        "unit": unit,
        "current_stock": current_stock,
        "avg_days_between_purchases": purchase_pattern["avg_days_between_purchases"],
        "avg_quantity_per_purchase": suggested_quantity,
        "avg_consumption_rate": avg_consumption_rate,
        "predicted_depletion_date": predicted_depletion_date,
        "days_until_depletion": days_until_depletion,
        "suggested_quantity": suggested_quantity,
        "confidence_level": confidence,
        "urgency": urgency,
        "data_points_count": total_data_points
    }


def analyze_all_user_items(
    db: Session,
    firebase_uid: str
) -> List[Dict]:
    """
    Analyze patterns for all frequently purchased items for a user
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        
    Returns:
        List[Dict]: List of pattern analyses for all items
    """
    from crud.purchase_log import get_frequently_purchased_items
    
    # Get all frequently purchased items
    frequent_items = get_frequently_purchased_items(
        db=db,
        firebase_uid=firebase_uid,
        days_back=90,
        min_purchases=2,
        limit=100
    )
    
    results = []
    
    for item in frequent_items:
        analysis = analyze_item_pattern(
            db=db,
            firebase_uid=firebase_uid,
            item_name=item["item_name"],
            category=item["category"]
        )
        
        if analysis:
            results.append(analysis)
    
    # Sort by urgency (urgent first)
    urgency_order = {
        UrgencyLevel.URGENT: 0,
        UrgencyLevel.THIS_WEEK: 1,
        UrgencyLevel.LATER: 2
    }
    
    results.sort(key=lambda x: urgency_order.get(x["urgency"], 3))
    
    logger.info(f"Analyzed {len(results)} items for user {firebase_uid}")
    return results


def generate_shopping_list(
    db: Session,
    firebase_uid: str,
    urgency_filter: Optional[str] = None
) -> Dict[str, List[Dict]]:
    """
    Generate smart shopping list based on pattern analysis
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        urgency_filter: Filter by urgency level (optional)
        
    Returns:
        Dict with categorized shopping items:
        {
            "urgent": [...],
            "this_week": [...],
            "later": [...]
        }
    """
    analyses = analyze_all_user_items(db, firebase_uid)
    
    shopping_list = {
        "urgent": [],
        "this_week": [],
        "later": []
    }
    
    for analysis in analyses:
        urgency = analysis["urgency"].value
        
        # Skip if filtering and doesn't match
        if urgency_filter and urgency != urgency_filter:
            continue
        
        item_info = {
            "item_name": analysis["item_name"],
            "category": analysis["category"],
            "suggested_quantity": analysis["suggested_quantity"],
            "unit": analysis["unit"],
            "current_stock": analysis["current_stock"],
            "predicted_depletion_date": analysis["predicted_depletion_date"].isoformat() if analysis["predicted_depletion_date"] else None,
            "confidence": analysis["confidence_level"].value,
            "reason": _generate_reason(analysis)
        }
        
        shopping_list[urgency].append(item_info)
    
    return shopping_list


def _generate_reason(analysis: Dict) -> str:
    """Generate human-readable reason for shopping suggestion"""
    
    if analysis["current_stock"] <= 0:
        return "Out of stock"
    
    days = int(analysis["days_until_depletion"])
    
    if days == 0:
        return "Running out today"
    elif days == 1:
        return "Will run out tomorrow"
    elif days <= 3:
        return f"Will run out in {days} days"
    elif analysis["avg_days_between_purchases"]:
        return f"Usually buy every {int(analysis['avg_days_between_purchases'])} days"
    else:
        return "Based on your usage pattern"
