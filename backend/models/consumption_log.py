# Consumption log model for tracking when items are used
# Used for pattern analysis and predictive shopping lists

from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base


class ConsumptionLog(Base):
    __tablename__ = "consumption_log"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to users
    firebase_uid = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True)
    
    # Item information
    item_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    quantity_consumed = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Dates for pattern analysis
    consumed_date = Column(Date, nullable=False)
    added_date = Column(Date, nullable=False)  # When the item was originally added
    days_lasted = Column(Integer, nullable=False)  # consumed_date - added_date
    
    # Reference to original inventory item (soft reference, can be null if item deleted)
    inventory_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Composite index for pattern queries
    __table_args__ = (
        # Index for querying user's consumption patterns by item
        # Index(f'ix_{__tablename__}_user_item', 'firebase_uid', 'item_name'),
    )
    
    def __repr__(self):
        return f"<ConsumptionLog(item={self.item_name}, lasted={self.days_lasted} days)>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "item_name": self.item_name,
            "category": self.category,
            "quantity_consumed": float(self.quantity_consumed),
            "unit": self.unit,
            "consumed_date": self.consumed_date.isoformat() if self.consumed_date else None,
            "days_lasted": self.days_lasted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

