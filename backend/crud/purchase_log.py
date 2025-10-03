# CRUD operations for PurchaseLog model

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import date, timedelta
import logging

from models.purchase_log import PurchaseLog

logger = logging.getLogger(__name__)


def create_purchase_log(
    db: Session,
    firebase_uid: str,
    item_name: str,
    category: str,
    quantity: float,
    unit: str,
    inventory_id: Optional[int] = None,
    purchase_date: Optional[date] = None
) -> PurchaseLog:
    """
    Create a purchase log entry when user adds items to inventory
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        item_name: Name of the item
        category: Item category
        quantity: Quantity purchased
        unit: Unit of measurement
        inventory_id: Reference to inventory item (optional)
        purchase_date: Date of purchase (defaults to today)
        
    Returns:
        PurchaseLog: Created purchase log entry
    """
    purchase_log = PurchaseLog(
        firebase_uid=firebase_uid,
        item_name=item_name,
        category=category,
        quantity_purchased=quantity,
        unit=unit,
        inventory_id=inventory_id,
        purchase_date=purchase_date or date.today()
    )
    
    db.add(purchase_log)
    db.commit()
    db.refresh(purchase_log)
    
    logger.info(f"Created purchase log for {item_name}: {quantity}{unit}")
    return purchase_log


def get_purchase_history(
    db: Session,
    firebase_uid: str,
    item_name: Optional[str] = None,
    category: Optional[str] = None,
    days_back: int = 90,
    limit: int = 100
) -> List[PurchaseLog]:
    """
    Get purchase history for a user, optionally filtered by item or category
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        item_name: Filter by item name (optional)
        category: Filter by category (optional)
        days_back: How many days back to look (default 90)
        limit: Maximum number of records to return
        
    Returns:
        List[PurchaseLog]: List of purchase logs, ordered by date (newest first)
    """
    cutoff_date = date.today() - timedelta(days=days_back)
    
    query = db.query(PurchaseLog).filter(
        and_(
            PurchaseLog.firebase_uid == firebase_uid,
            PurchaseLog.purchase_date >= cutoff_date
        )
    )
    
    if item_name:
        query = query.filter(PurchaseLog.item_name.ilike(item_name))
    
    if category:
        query = query.filter(PurchaseLog.category == category)
    
    query = query.order_by(desc(PurchaseLog.purchase_date))
    query = query.limit(limit)
    
    return query.all()


def get_item_purchase_pattern(
    db: Session,
    firebase_uid: str,
    item_name: str,
    min_records: int = 3,
    max_records: int = 10
) -> Optional[dict]:
    """
    Analyze purchase pattern for a specific item
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        item_name: Name of the item to analyze
        min_records: Minimum purchase records required
        max_records: Maximum records to consider (recent ones)
        
    Returns:
        dict | None: Purchase pattern analysis or None if insufficient data
        {
            "purchase_count": int,
            "avg_days_between_purchases": float,
            "avg_quantity_per_purchase": float,
            "last_purchase_date": date,
            "purchase_logs": List[PurchaseLog]
        }
    """
    # Get recent purchases for this item
    purchases = db.query(PurchaseLog).filter(
        and_(
            PurchaseLog.firebase_uid == firebase_uid,
            PurchaseLog.item_name.ilike(item_name)
        )
    ).order_by(desc(PurchaseLog.purchase_date)).limit(max_records).all()
    
    if len(purchases) < min_records:
        logger.debug(f"Insufficient purchase data for {item_name}: {len(purchases)} records")
        return None
    
    # Reverse to get chronological order for interval calculation
    purchases = list(reversed(purchases))
    
    # Calculate days between purchases
    intervals = []
    for i in range(len(purchases) - 1):
        days = (purchases[i + 1].purchase_date - purchases[i].purchase_date).days
        if days > 0:  # Ignore same-day purchases
            intervals.append(days)
    
    # Calculate averages
    avg_days = sum(intervals) / len(intervals) if intervals else None
    avg_quantity = sum(p.quantity_purchased for p in purchases) / len(purchases)
    
    return {
        "purchase_count": len(purchases),
        "avg_days_between_purchases": avg_days,
        "avg_quantity_per_purchase": float(avg_quantity),
        "last_purchase_date": purchases[-1].purchase_date,
        "purchase_logs": purchases
    }


def get_frequently_purchased_items(
    db: Session,
    firebase_uid: str,
    days_back: int = 90,
    min_purchases: int = 2,
    limit: int = 50
) -> List[dict]:
    """
    Get list of frequently purchased items for pattern analysis
    
    Args:
        db: Database session
        firebase_uid: User's Firebase UID
        days_back: Look back period in days
        min_purchases: Minimum purchase count to be considered
        limit: Maximum items to return
        
    Returns:
        List[dict]: List of items with purchase counts
        [
            {
                "item_name": str,
                "category": str,
                "purchase_count": int,
                "last_purchase_date": date
            }
        ]
    """
    cutoff_date = date.today() - timedelta(days=days_back)
    
    # Query to get item purchase counts
    from sqlalchemy import func
    
    results = db.query(
        PurchaseLog.item_name,
        PurchaseLog.category,
        func.count(PurchaseLog.id).label('purchase_count'),
        func.max(PurchaseLog.purchase_date).label('last_purchase_date')
    ).filter(
        and_(
            PurchaseLog.firebase_uid == firebase_uid,
            PurchaseLog.purchase_date >= cutoff_date
        )
    ).group_by(
        PurchaseLog.item_name,
        PurchaseLog.category
    ).having(
        func.count(PurchaseLog.id) >= min_purchases
    ).order_by(
        desc('purchase_count')
    ).limit(limit).all()
    
    return [
        {
            "item_name": r.item_name,
            "category": r.category,
            "purchase_count": r.purchase_count,
            "last_purchase_date": r.last_purchase_date
        }
        for r in results
    ]
