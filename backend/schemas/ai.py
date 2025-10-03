# Pydantic schemas for AI endpoints


from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class DetectedItem(BaseModel):
    # Item detected from receipt image
    item_name: str = Field(..., description="Item name")
    quantity: float = Field(..., gt=0, description="Quantity")
    unit: str = Field(..., description="Unit (kg, liters, pieces, etc.)")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    category: str = Field(default="others", description="Item category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "tomatoes",
                "quantity": 2.0,
                "unit": "kg",
                "confidence": 0.95,
                "category": "vegetables"
            }
        }


class ReceiptParseResponse(BaseModel):
    # Response from receipt parsing
    success: bool
    items_detected: int
    items: List[DetectedItem]
    message: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "items_detected": 3,
                "items": [
                    {
                        "item_name": "tomatoes",
                        "quantity": 2.0,
                        "unit": "kg",
                        "confidence": 0.95,
                        "category": "vegetables"
                    }
                ],
                "message": "Successfully detected 3 items from receipt"
            }
        }


class RecipeFilters(BaseModel):
    # Filters for recipe generation
    cooking_time: Optional[int] = Field(default=45, ge=10, le=180, description="Max cooking time in minutes")
    meal_type: Optional[str] = Field(default="any", pattern="^(breakfast|lunch|dinner|snack|any)$")
    cuisine: Optional[str] = Field(default="Indian", description="Preferred cuisine")
    must_use_items: Optional[List[str]] = Field(default=None, description="Items that must be used in recipe")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cooking_time": 30,
                "meal_type": "dinner",
                "cuisine": "North Indian",
                "must_use_items": ["paneer", "tomatoes"]
            }
        }


class RecipeIngredient(BaseModel):
    # Recipe ingredient
    item: str
    quantity: float
    unit: str
    available: bool
    note: Optional[str] = None


class RecipeNutrition(BaseModel):
    # Nutrition information
    calories: int
    protein: int
    carbs: int
    fat: int
    fiber: int


class RecipeResponse(BaseModel):
    # Generated recipe response
    recipe_name: str
    description: str
    cooking_time_minutes: int
    difficulty: str
    cuisine: str
    servings: int
    ingredients: List[RecipeIngredient]
    instructions: List[str]
    tips: List[str]
    nutrition: RecipeNutrition
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipe_name": "Paneer Butter Masala",
                "description": "Rich and creamy North Indian curry",
                "cooking_time_minutes": 30,
                "difficulty": "easy",
                "cuisine": "North Indian",
                "servings": 4,
                "ingredients": [
                    {
                        "item": "paneer",
                        "quantity": 200,
                        "unit": "grams",
                        "available": True
                    }
                ],
                "instructions": ["Step 1...", "Step 2..."],
                "tips": ["Tip 1...", "Tip 2..."],
                "nutrition": {
                    "calories": 320,
                    "protein": 15,
                    "carbs": 18,
                    "fat": 22,
                    "fiber": 3
                }
            }
        }

