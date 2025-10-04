# Pydantic schemas for shopping list and pattern analysis endpoints

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ShoppingItemResponse(BaseModel):
    """Individual shopping item suggestion"""
    item_name: str
    category: str
    suggested_quantity: float
    unit: str
    current_stock: float
    predicted_depletion_date: Optional[str] = None
    confidence: str  # low, medium, high
    reason: str  # Human-readable reason for suggestion
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "milk",
                "category": "dairy",
                "suggested_quantity": 2.0,
                "unit": "liters",
                "current_stock": 0.5,
                "predicted_depletion_date": "2025-10-05",
                "confidence": "high",
                "reason": "Will run out in 2 days"
            }
        }


class ShoppingListResponse(BaseModel):
    """Grouped shopping list by urgency"""
    urgent: List[ShoppingItemResponse] = Field(default_factory=list, description="Buy today/tomorrow")
    this_week: List[ShoppingItemResponse] = Field(default_factory=list, description="Buy within 7 days")
    later: List[ShoppingItemResponse] = Field(default_factory=list, description="No immediate rush")
    generated_at: str
    total_items: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "urgent": [
                    {
                        "item_name": "milk",
                        "category": "dairy",
                        "suggested_quantity": 2.0,
                        "unit": "liters",
                        "current_stock": 0.0,
                        "predicted_depletion_date": None,
                        "confidence": "high",
                        "reason": "Out of stock"
                    }
                ],
                "this_week": [],
                "later": [],
                "generated_at": "2025-10-03T10:30:00",
                "total_items": 1
            }
        }


class PredictionResponse(BaseModel):
    """Single item pattern prediction"""
    id: int
    item_name: str
    category: str
    unit: str
    current_stock: float
    avg_days_between_purchases: Optional[float] = None
    avg_quantity_per_purchase: Optional[float] = None
    avg_consumption_rate: Optional[float] = None
    predicted_depletion_date: Optional[str] = None
    days_until_depletion: Optional[float] = None
    suggested_quantity: Optional[float] = None
    confidence_level: str
    urgency: str
    data_points_count: int
    last_analyzed: str
    
    class Config:
        from_attributes = True


class PatternInsightsResponse(BaseModel):
    """Detailed pattern insights for an item"""
    item_name: str
    category: str
    current_stock: float
    unit: str
    pattern: dict  # Purchase and consumption patterns
    prediction: dict  # Predicted depletion and suggestions
    last_analyzed: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "rice",
                "category": "staples",
                "current_stock": 3.0,
                "unit": "kg",
                "pattern": {
                    "purchase_frequency_days": 14.5,
                    "avg_quantity_purchased": 5.0,
                    "consumption_rate_per_day": 0.35,
                    "data_points": 8
                },
                "prediction": {
                    "depletion_date": "2025-10-12",
                    "suggested_quantity": 5.0,
                    "urgency": "this_week",
                    "confidence": "high"
                },
                "last_analyzed": "2025-10-03T06:00:00"
            }
        }


class AnalyzeRequest(BaseModel):
    """Request to trigger pattern analysis"""
    force_refresh: bool = Field(
        default=False,
        description="Force re-analysis even if recent analysis exists"
    )


class AnalyzeResponse(BaseModel):
    """Response from pattern analysis"""
    message: str
    items_analyzed: int
    predictions_saved: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Pattern analysis completed successfully",
                "items_analyzed": 15,
                "predictions_saved": 12
            }
        }
