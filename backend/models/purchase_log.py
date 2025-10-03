# Purchase log model for tracking when items are added to inventory
# Used for pattern analysis to determine purchase frequency

from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base


class PurchaseLog(Base):
    __tablename__ = "purchase_log"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to users
    firebase_uid = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True)
    
    # Item information
    item_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    quantity_purchased = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Purchase tracking
    purchase_date = Column(Date, nullable=False, server_default=func.current_date())
    
    # Reference to inventory item (soft reference, can be null if item deleted)
    inventory_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Composite index for pattern queries
    __table_args__ = (
        # Index for querying user's purchase patterns by item
        # Index('ix_purchase_log_user_item', 'firebase_uid', 'item_name'),
    )
    
    def __repr__(self):
        return f"<PurchaseLog(item={self.item_name}, quantity={self.quantity_purchased}{self.unit}, date={self.purchase_date})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "item_name": self.item_name,
            "category": self.category,
            "quantity_purchased": float(self.quantity_purchased),
            "unit": self.unit,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "inventory_id": self.inventory_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
