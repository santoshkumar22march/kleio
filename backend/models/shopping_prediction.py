# Shopping prediction model for storing pattern analysis results
# Contains smart predictions about when items will run out and what to buy

from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from database import Base


class ConfidenceLevel(str, enum.Enum):
    LOW = "low"        # Less than 3 data points
    MEDIUM = "medium"  # 3-4 data points
    HIGH = "high"      # 5+ data points


class UrgencyLevel(str, enum.Enum):
    URGENT = "urgent"          # Buy today/tomorrow
    THIS_WEEK = "this_week"    # Buy within 7 days
    LATER = "later"            # No rush


class ShoppingPrediction(Base):
    __tablename__ = "shopping_predictions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to users
    firebase_uid = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True)
    
    # Item information
    item_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Pattern metrics (calculated from historical data)
    avg_days_between_purchases = Column(Float, nullable=True)  # How often item is bought
    avg_quantity_per_purchase = Column(Float, nullable=True)   # Typical purchase quantity
    avg_consumption_rate = Column(Float, nullable=True)        # Quantity consumed per day
    
    # Predictions
    predicted_depletion_date = Column(Date, nullable=True)     # When item will run out
    suggested_quantity = Column(Float, nullable=True)          # Recommended purchase amount
    confidence_level = Column(SQLEnum(ConfidenceLevel), default=ConfidenceLevel.LOW)
    urgency = Column(SQLEnum(UrgencyLevel), default=UrgencyLevel.LATER)
    
    # Metadata
    last_analyzed = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    data_points_count = Column(Integer, default=0)             # Number of logs used for analysis
    current_stock = Column(Float, default=0)                   # Current quantity in inventory
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        # Composite index for querying user's predictions by urgency
        # Index('ix_shopping_predictions_user_urgency', 'firebase_uid', 'urgency'),
    )
    
    def __repr__(self):
        return f"<ShoppingPrediction(item={self.item_name}, urgency={self.urgency}, confidence={self.confidence_level})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "item_name": self.item_name,
            "category": self.category,
            "unit": self.unit,
            "avg_days_between_purchases": self.avg_days_between_purchases,
            "avg_quantity_per_purchase": self.avg_quantity_per_purchase,
            "avg_consumption_rate": self.avg_consumption_rate,
            "predicted_depletion_date": self.predicted_depletion_date.isoformat() if self.predicted_depletion_date else None,
            "suggested_quantity": self.suggested_quantity,
            "confidence_level": self.confidence_level.value,
            "urgency": self.urgency.value,
            "last_analyzed": self.last_analyzed.isoformat() if self.last_analyzed else None,
            "data_points_count": self.data_points_count,
            "current_stock": self.current_stock,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
