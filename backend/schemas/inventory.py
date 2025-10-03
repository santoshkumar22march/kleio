"""
Pydantic schemas for Inventory model validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class InventoryCreate(BaseModel):
    """Schema for creating a new inventory item"""
    item_name: str = Field(..., min_length=1, max_length=100, description="Name of the item")
    category: str = Field(..., min_length=1, max_length=50, description="Category (vegetables, fruits, etc.)")
    quantity: Decimal = Field(..., gt=0, decimal_places=2, description="Quantity amount")
    unit: str = Field(..., min_length=1, max_length=20, description="Unit (kg, liters, pieces, etc.)")
    expiry_date: Optional[date] = Field(default=None, description="Expiry date (optional)")
    photo_url: Optional[str] = Field(default=None, max_length=255)
    
    @field_validator('item_name', 'category', 'unit')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Remove leading/trailing whitespace"""
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "Tomatoes",
                "category": "vegetables",
                "quantity": 2.0,
                "unit": "kg",
                "expiry_date": "2025-10-10"
            }
        }


class InventoryUpdate(BaseModel):
    """Schema for updating inventory item"""
    quantity: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    expiry_date: Optional[date] = None
    status: Optional[str] = Field(default=None, pattern="^(active|consumed|expired|discarded)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity": 1.5,
                "expiry_date": "2025-10-12"
            }
        }


class InventoryMarkUsed(BaseModel):
    """Schema for marking item as used/consumed"""
    quantity_used: Optional[Decimal] = Field(default=None, gt=0, description="Amount consumed (optional, defaults to all)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "quantity_used": 0.5
            }
        }


class InventoryResponse(BaseModel):
    """Schema for inventory item response"""
    id: int
    firebase_uid: str
    item_name: str
    category: str
    quantity: float
    unit: str
    added_date: date
    expiry_date: Optional[date]
    status: str
    photo_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "firebase_uid": "abc123",
                "item_name": "Tomatoes",
                "category": "vegetables",
                "quantity": 2.0,
                "unit": "kg",
                "added_date": "2025-10-03",
                "expiry_date": "2025-10-10",
                "status": "active",
                "photo_url": None,
                "created_at": "2025-10-03T10:00:00"
            }
        }


class BulkInventoryCreate(BaseModel):
    """Schema for bulk adding inventory items (from photo detection)"""
    items: List[InventoryCreate] = Field(..., min_length=1, max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "item_name": "Tomatoes",
                        "category": "vegetables",
                        "quantity": 2.0,
                        "unit": "kg"
                    },
                    {
                        "item_name": "Onions",
                        "category": "vegetables",
                        "quantity": 1.0,
                        "unit": "kg"
                    }
                ]
            }
        }

