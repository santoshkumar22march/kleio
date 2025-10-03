# Inventory model for storing household items


from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base


class ItemStatus(str, enum.Enum):
    # Status of inventory items
    ACTIVE = "active"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    DISCARDED = "discarded"


class Inventory(Base):
    __tablename__ = "inventory"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to users
    firebase_uid = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True)
    
    # Item details
    item_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # vegetables, fruits, dairy, staples, etc.
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)  # kg, grams, liters, ml, pieces, dozens
    
    # Dates
    added_date = Column(Date, server_default=func.current_date())
    expiry_date = Column(Date, nullable=True)
    
    # Status
    status = Column(SQLEnum(ItemStatus), default=ItemStatus.ACTIVE, index=True)
    
    # Optional photo
    photo_url = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        # Composite index for common query: get user's active items
        # Index(f'ix_{__tablename__}_user_status', 'firebase_uid', 'status'),
    )
    
    def __repr__(self):
        return f"<Inventory(id={self.id}, item={self.item_name}, quantity={self.quantity}{self.unit})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "item_name": self.item_name,
            "category": self.category,
            "quantity": float(self.quantity),
            "unit": self.unit,
            "added_date": self.added_date.isoformat() if self.added_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "status": self.status.value,
            "photo_url": self.photo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

