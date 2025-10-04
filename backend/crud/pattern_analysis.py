# CRUD operations for pattern analysis and shopping predictions

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime
import logging

from models.shopping_prediction import ShoppingPrediction, UrgencyLevel, ConfidenceLevel
from utils.pattern_analyzer import analyze_item_pattern, analyze_all_user_items

logger = logging.getLogger(__name__)


def save_or_update_prediction(
    db: Session,
    firebase_uid: str,
    analysis_result: dict
) -> ShoppingPrediction:
    """
    Save or update a shopping prediction based on pattern analysis
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        analysis_result: Result from analyze_item_pattern()
        
    Returns:
        ShoppingPrediction: Created or updated prediction
    """
    # Check if prediction already exists for this item
    existing = db.query(ShoppingPrediction).filter(
        and_(
            ShoppingPrediction.firebase_uid == firebase_uid,
            ShoppingPrediction.item_name.ilike(analysis_result["item_name"])
        )
    ).first()
    
    if existing:
        # Update existing prediction
        existing.category = analysis_result["category"]
        existing.unit = analysis_result["unit"]
        existing.avg_days_between_purchases = analysis_result["avg_days_between_purchases"]
        existing.avg_quantity_per_purchase = analysis_result["avg_quantity_per_purchase"]
        existing.avg_consumption_rate = analysis_result["avg_consumption_rate"]
        existing.predicted_depletion_date = analysis_result["predicted_depletion_date"]
        existing.days_until_depletion = analysis_result["days_until_depletion"]
        existing.suggested_quantity = analysis_result["suggested_quantity"]
        existing.confidence_level = analysis_result["confidence_level"]
        existing.urgency = analysis_result["urgency"]
        existing.data_points_count = analysis_result["data_points_count"]
        existing.current_stock = analysis_result["current_stock"]
        existing.last_analyzed = datetime.now()
        
        db.commit()
        db.refresh(existing)
        logger.debug(f"Updated prediction for {analysis_result['item_name']}")
        return existing
    else:
        # Create new prediction
        new_prediction = ShoppingPrediction(
            firebase_uid=firebase_uid,
            item_name=analysis_result["item_name"],
            category=analysis_result["category"],
            unit=analysis_result["unit"],
            avg_days_between_purchases=analysis_result["avg_days_between_purchases"],
            avg_quantity_per_purchase=analysis_result["avg_quantity_per_purchase"],
            avg_consumption_rate=analysis_result["avg_consumption_rate"],
            predicted_depletion_date=analysis_result["predicted_depletion_date"],
            days_until_depletion=analysis_result["days_until_depletion"],
            suggested_quantity=analysis_result["suggested_quantity"],
            confidence_level=analysis_result["confidence_level"],
            urgency=analysis_result["urgency"],
            data_points_count=analysis_result["data_points_count"],
            current_stock=analysis_result["current_stock"]
        )
        
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)
        logger.debug(f"Created prediction for {analysis_result['item_name']}")
        return new_prediction


def analyze_and_save_user_patterns(
    db: Session,
    firebase_uid: str
) -> int:
    """
    Analyze all items for a user and save predictions to database
    
    This is called by the background job to update predictions daily
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        
    Returns:
        int: Number of predictions saved/updated
    """
    logger.info(f"Analyzing patterns for user {firebase_uid}")
    
    # Analyze all user items
    analyses = analyze_all_user_items(db, firebase_uid)
    
    # Save each prediction
    count = 0
    for analysis in analyses:
        try:
            save_or_update_prediction(db, firebase_uid, analysis)
            count += 1
        except Exception as e:
            logger.error(f"Failed to save prediction for {analysis['item_name']}: {e}")
    
    logger.info(f"Saved {count} predictions for user {firebase_uid}")
    return count


def get_user_predictions(
    db: Session,
    firebase_uid: str,
    urgency: Optional[UrgencyLevel] = None,
    min_confidence: Optional[ConfidenceLevel] = None,
    limit: int = 50
) -> List[ShoppingPrediction]:
    """
    Get shopping predictions for a user
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        urgency: Filter by urgency level (optional)
        min_confidence: Minimum confidence level (optional)
        limit: Maximum predictions to return
        
    Returns:
        List[ShoppingPrediction]: List of predictions
    """
    query = db.query(ShoppingPrediction).filter(
        ShoppingPrediction.firebase_uid == firebase_uid
    )
    
    if urgency:
        query = query.filter(ShoppingPrediction.urgency == urgency)
    
    if min_confidence:
        # Filter by minimum confidence (assumes enum ordering)
        confidence_order = {
            ConfidenceLevel.LOW: 0,
            ConfidenceLevel.MEDIUM: 1,
            ConfidenceLevel.HIGH: 2
        }
        min_level = confidence_order.get(min_confidence, 0)
        
        if min_level > 0:
            query = query.filter(
                ShoppingPrediction.confidence_level.in_([
                    level for level, order in confidence_order.items() if order >= min_level
                ])
            )
    
    # Order by urgency (most urgent first)
    query = query.order_by(
        ShoppingPrediction.urgency,
        ShoppingPrediction.predicted_depletion_date
    )
    
    return query.limit(limit).all()


def get_shopping_list_grouped(
    db: Session,
    firebase_uid: str
) -> dict:
    """
    Get shopping list grouped by urgency
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        
    Returns:
        dict: Shopping list grouped by urgency
        {
            "urgent": [...],
            "this_week": [...],
            "later": [...]
        }
    """
    all_predictions = get_user_predictions(db, firebase_uid, limit=100)
    
    grouped = {
        "urgent": [],
        "this_week": [],
        "later": []
    }
    
    for pred in all_predictions:
        urgency_key = pred.urgency.value
        grouped[urgency_key].append(pred)
    
    return grouped


def delete_old_predictions(
    db: Session,
    firebase_uid: str
) -> int:
    """
    Delete predictions for items that user no longer purchases
    (no purchase in last 90 days)
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        
    Returns:
        int: Number of predictions deleted
    """
    from datetime import date, timedelta
    from models.purchase_log import PurchaseLog
    
    cutoff_date = date.today() - timedelta(days=90)
    
    # Get all predictions for user
    predictions = db.query(ShoppingPrediction).filter(
        ShoppingPrediction.firebase_uid == firebase_uid
    ).all()
    
    deleted_count = 0
    
    for pred in predictions:
        # Check if there are recent purchases
        recent_purchase = db.query(PurchaseLog).filter(
            and_(
                PurchaseLog.firebase_uid == firebase_uid,
                PurchaseLog.item_name.ilike(pred.item_name),
                PurchaseLog.purchase_date >= cutoff_date
            )
        ).first()
        
        if not recent_purchase:
            # No recent purchases, delete prediction
            db.delete(pred)
            deleted_count += 1
    
    db.commit()
    logger.info(f"Deleted {deleted_count} old predictions for user {firebase_uid}")
    return deleted_count


def get_pattern_insights(
    db: Session,
    firebase_uid: str,
    item_name: str
) -> Optional[dict]:
    """
    Get detailed pattern insights for a specific item
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        item_name: Item name
        
    Returns:
        dict | None: Detailed insights or None if not found
    """
    from models.inventory import Inventory, ItemStatus
    
    # Get current inventory item
    current_item = db.query(Inventory).filter(
        and_(
            Inventory.firebase_uid == firebase_uid,
            Inventory.item_name.ilike(item_name),
            Inventory.status == ItemStatus.ACTIVE
        )
    ).first()
    
    if not current_item:
        return None
    
    # Get or create prediction
    prediction = db.query(ShoppingPrediction).filter(
        and_(
            ShoppingPrediction.firebase_uid == firebase_uid,
            ShoppingPrediction.item_name.ilike(item_name)
        )
    ).first()
    
    if not prediction:
        # Analyze on-demand if no prediction exists
        analysis = analyze_item_pattern(
            db=db,
            firebase_uid=firebase_uid,
            item_name=item_name,
            category=current_item.category
        )
        
        if analysis:
            prediction = save_or_update_prediction(db, firebase_uid, analysis)
    
    if not prediction:
        return None
    
    return {
        "item_name": prediction.item_name,
        "category": prediction.category,
        "current_stock": prediction.current_stock,
        "unit": prediction.unit,
        "pattern": {
            "purchase_frequency_days": prediction.avg_days_between_purchases,
            "avg_quantity_purchased": prediction.avg_quantity_per_purchase,
            "consumption_rate_per_day": prediction.avg_consumption_rate,
            "data_points": prediction.data_points_count
        },
        "prediction": {
            "depletion_date": prediction.predicted_depletion_date.isoformat() if prediction.predicted_depletion_date else None,
            "suggested_quantity": prediction.suggested_quantity,
            "urgency": prediction.urgency.value,
            "confidence": prediction.confidence_level.value
        },
        "last_analyzed": prediction.last_analyzed.isoformat() if prediction.last_analyzed else None
    }
