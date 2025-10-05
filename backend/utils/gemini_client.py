# Gemini AI client for receipt parsing and recipe generation


from google import genai
from google.genai import types
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    # Gemini AI client for Kleio.ai
    
    # Use Gemini 2.5 Flash-Lite - fastest and most cost-efficient
    MODEL_ID = "gemini-2.5-flash-lite"
    
    def __init__(self):
        # Initialize Gemini client
        try:
            self.client = genai.Client(api_key=settings.gemini_api_key)
            logger.info(f"✅ Gemini client initialized with model: {self.MODEL_ID}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    async def parse_receipt(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> List[Dict]:
        """
        Parse receipt/bill image to extract grocery items
        
        Args:
            image_bytes: Image bytes from uploaded receipt
            mime_type: Image MIME type (image/jpeg, image/png, etc.)
            
        Returns:
            List of detected items with name, quantity, unit, confidence
            
        Example:
            [
                {"name": "tomatoes", "quantity": 2.0, "unit": "kg", "confidence": 0.95},
                {"name": "onions", "quantity": 1.0, "unit": "kg", "confidence": 0.90}
            ]
        """
        
        prompt = """
You are an expert at reading grocery receipts and bills from Indian stores.

Analyze this receipt/bill image and extract ALL grocery items purchased.

For each item, identify:
1. Item name (in English, lowercase)
2. Quantity (numeric value)
3. Unit (kg, grams, liters, ml, pieces, packets, etc.)
4. Confidence score (0.0 to 1.0)
5. Category (vegetables, fruits, dairy, staples, etc.)
6. Estimated shelf life in days (integer, e.g., 7 for milk, 90 for rice)

IMPORTANT RULES:
- Focus ONLY on grocery/food items.
- Convert quantities to standard units.
- Estimate shelf life based on typical household storage.
- Estimate shelf life should be based on Inian products and Indian household storage, Indian weather conditions.
- For example, pasteurized milk has a shelf life of 2 days in India, rice has a shelf life of 365 days in India.
Return ONLY valid JSON array (no markdown, no explanation):
[
  {
    "item_name": "tomatoes",
    "quantity": 2.0,
    "unit": "kg",
    "confidence": 0.95,
    "category": "vegetables",
    "estimated_shelf_life_days": 7
  },
  {
    "item_name": "toor dal",
    "quantity": 1.0,
    "unit": "kg",
    "confidence": 0.90,
    "category": "pulses",
    "estimated_shelf_life_days": 365
  }
]

Categories: vegetables, fruits, dairy, staples, pulses, spices, snacks, beverages, meat, seafood, bakery, frozen, oils, condiments, others

If you cannot read the receipt clearly, return an empty array: []
"""
        
        try:
            logger.info("📸 Sending receipt image to Gemini for parsing...")
            
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    types.Part.from_text(text=prompt)
                ],
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for more accurate extraction
                    top_p=0.95,
                    top_k=40,
                    response_mime_type="application/json",  # Request JSON response
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            logger.debug(f"Raw Gemini response: {response_text}")
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                # Remove first and last lines (```json and ```)
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            # Parse JSON
            items = json.loads(response_text)
            
            if not isinstance(items, list):
                logger.error("Response is not a list")
                return []
            
            logger.info(f"✅ Detected {len(items)} items from receipt")
            
            # Validate and clean items
            validated_items = []
            for item in items:
                # Support both 'name' and 'item_name' for backward compatibility
                if "name" in item and "item_name" not in item:
                    item["item_name"] = item.pop("name")
                
                if all(key in item for key in ["item_name", "quantity", "unit"]):
                    # Set default category if missing
                    if "category" not in item:
                        item["category"] = "others"
                    
                    # Set default confidence if missing
                    if "confidence" not in item:
                        item["confidence"] = 0.7
                    
                    validated_items.append(item)
                else:
                    logger.warning(f"Skipping invalid item: {item}")
            
            return validated_items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return []
        except Exception as e:
            logger.error(f"Error parsing receipt: {e}")
            return []
    
    async def generate_recipe(
        self,
        available_items: List[str],
        dietary_preferences: Dict[str, bool],
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Generate recipe based on available inventory
        
        Args:
            available_items: List of items user has in inventory
            dietary_preferences: User's dietary restrictions
            filters: Optional filters (cooking_time, meal_type, cuisine)
            
        Returns:
            Recipe with ingredients, instructions, nutrition info
        """
        
        # Extract filters
        cooking_time = filters.get("cooking_time", 45) if filters else 45
        meal_type = filters.get("meal_type", "any") if filters else "any"
        cuisine = filters.get("cuisine", "Indian") if filters else "Indian"
        
        # Build dietary restrictions text
        dietary_text = []
        if dietary_preferences.get("vegetarian"):
            dietary_text.append("vegetarian (no meat, no eggs)")
        if dietary_preferences.get("vegan"):
            dietary_text.append("vegan (no animal products)")
        if dietary_preferences.get("diabetic"):
            dietary_text.append("diabetic-friendly (low sugar, low GI)")
        if dietary_preferences.get("gluten_free"):
            dietary_text.append("gluten-free")
        
        dietary_str = ", ".join(dietary_text) if dietary_text else "no restrictions"
        
        prompt = f"""
You are an expert Indian home cooking assistant.

AVAILABLE INGREDIENTS IN USER'S KITCHEN:
{', '.join(available_items)}

USER REQUIREMENTS:
- Cooking time: Maximum {cooking_time} minutes
- Meal type: {meal_type}
- Cuisine: {cuisine}
- Dietary restrictions: {dietary_str}

Generate ONE delicious recipe that:
1. Uses MOSTLY ingredients from the available list
2. Is practical for Indian home cooking
3. Meets the time and dietary requirements
4. Can have 2-3 common ingredients not in the list (oil, salt, spices) - mark them clearly

CRITICAL RULES:
- ALL ingredients MUST have quantity and unit (never null/None)
- Use numeric quantities only (e.g., 200 not "200" or null)
- Common units: grams, kg, ml, liters, pieces, tablespoons, teaspoons, cups
- If quantity is approximate, use reasonable numbers (e.g., "to taste" → 1 teaspoon)

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "recipe_name": "Paneer Butter Masala",
  "description": "Rich and creamy North Indian curry",
  "cooking_time_minutes": 30,
  "difficulty": "easy",
  "cuisine": "North Indian",
  "servings": 4,
  "ingredients": [
    {{
      "item": "paneer",
      "quantity": 200,
      "unit": "grams",
      "available": true
    }},
    {{
      "item": "tomatoes",
      "quantity": 3,
      "unit": "pieces",
      "available": true
    }},
    {{
      "item": "oil",
      "quantity": 2,
      "unit": "tablespoons",
      "available": false
    }},
    {{
      "item": "salt",
      "quantity": 1,
      "unit": "teaspoon",
      "available": false
    }}
  ],
  "instructions": [
    "Cut paneer into cubes and lightly fry until golden",
    "Blend tomatoes into smooth puree",
    "Heat oil, add spices, then tomato puree",
    "Add paneer and simmer for 10 minutes",
    "Garnish and serve hot"
  ],
  "tips": [
    "Don't overcook paneer or it becomes rubbery",
    "Add kasuri methi for authentic flavor"
  ],
  "nutrition": {{
    "calories": 320,
    "protein": 15,
    "carbs": 18,
    "fat": 22,
    "fiber": 3
  }}
}}

REMEMBER: Every ingredient MUST have numeric quantity and unit. No null/None values allowed!
"""
        
        try:
            logger.info("🍳 Generating recipe with Gemini...")
            
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=[types.Part.from_text(text=prompt)],
                config=types.GenerateContentConfig(
                    temperature=0.7,  # Higher for creativity
                    top_p=0.95,
                    top_k=40,
                    response_mime_type="application/json",  # Request JSON response
                )
            )
            
            # Parse response
            response_text = response.text.strip()
            logger.debug(f"Raw recipe response: {response_text[:200]}...")
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            # Parse JSON
            recipe = json.loads(response_text)
            
            # Validate and fix ingredients
            if "ingredients" in recipe:
                fixed_ingredients = []
                for ing in recipe["ingredients"]:
                    # Fix missing or null quantities
                    if ing.get("quantity") is None or ing.get("quantity") == "":
                        # Assign default quantity based on item type
                        if "salt" in ing.get("item", "").lower() or "spice" in ing.get("item", "").lower():
                            ing["quantity"] = 1
                            ing["unit"] = "teaspoon"
                        elif "oil" in ing.get("item", "").lower():
                            ing["quantity"] = 2
                            ing["unit"] = "tablespoons"
                        else:
                            ing["quantity"] = 100
                            ing["unit"] = "grams"
                        logger.warning(f"Fixed missing quantity for {ing['item']}")
                    
                    # Ensure quantity is numeric
                    try:
                        ing["quantity"] = float(ing["quantity"])
                    except (ValueError, TypeError):
                        ing["quantity"] = 1.0
                        logger.warning(f"Fixed invalid quantity for {ing['item']}")
                    
                    # Set default unit if missing
                    if not ing.get("unit"):
                        ing["unit"] = "pieces"
                    
                    # Set default available status
                    if "available" not in ing:
                        ing["available"] = False
                    
                    fixed_ingredients.append(ing)
                
                recipe["ingredients"] = fixed_ingredients
            
            logger.info(f"✅ Generated recipe: {recipe.get('recipe_name')}")
            return recipe
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse recipe JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError("Failed to generate valid recipe")
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            raise


# Singleton instance
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

