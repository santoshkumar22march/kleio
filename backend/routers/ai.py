from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import date, timedelta

from database import get_db
from utils.auth import get_current_user
from utils.gemini_client import get_gemini_client
from schemas.ai import (
    ReceiptParseResponse,
    DetectedItem,
    RecipeFilters,
    RecipeResponse
)
from schemas.inventory import BulkInventoryCreate, InventoryCreate
from crud.inventory import create_inventory_item, get_user_inventory
from crud.user import get_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Features"])


@router.post(
    "/parse-receipt",
    response_model=ReceiptParseResponse,
    summary="Parse receipt/bill image",
    description="Upload receipt/bill image to detect purchased grocery items using AI"
)
async def parse_receipt(
    file: UploadFile = File(..., description="Receipt/bill image (JPEG, PNG, WebP)"),
    firebase_uid: str = Depends(get_current_user)
):
    """
    Parse receipt/bill image to extract grocery items
    
    - Upload image of grocery receipt or bill
    - AI detects items, quantities, and units
    - Returns detected items for user confirmation
    - Items are NOT automatically added to inventory
    """
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, WebP)"
        )
    
    # Validate file size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    contents = await file.read()
    
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    
    logger.info(f"📸 Processing receipt image for user {firebase_uid}: {file.filename}")
    
    try:
        # Get Gemini client
        gemini = get_gemini_client()
        
        # Parse receipt
        detected_items = await gemini.parse_receipt(
            image_bytes=contents,
            mime_type=file.content_type
        )
        
        if not detected_items:
            return ReceiptParseResponse(
                success=False,
                items_detected=0,
                items=[],
                message="Could not detect any grocery items from the receipt. Please ensure the image is clear and contains grocery items."
            )
        
        # Convert to Pydantic models
        items = [DetectedItem(**item) for item in detected_items]
        
        logger.info(f"✅ Detected {len(items)} items from receipt")
        
        return ReceiptParseResponse(
            success=True,
            items_detected=len(items),
            items=items,
            message=f"Successfully detected {len(items)} items from receipt. Review and confirm to add to inventory."
        )
        
    except Exception as e:
        logger.error(f"Error parsing receipt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse receipt: {str(e)}"
        )


@router.post(
    "/confirm-receipt-items",
    status_code=status.HTTP_201_CREATED,
    summary="Confirm and add detected items",
    description="Confirm detected items from receipt and add them to inventory. Updates existing items if already present."
)
async def confirm_receipt_items(
    items_data: BulkInventoryCreate,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirm detected items and add to inventory
    
    - If item already exists (active status, same name): Updates quantity (adds to existing)
    - If item doesn't exist: Creates new entry
    - Case-insensitive matching (Tomatoes = tomatoes)
    
    User can review, edit quantities, and confirm items
    before they are added to inventory
    """
    
    logger.info(f"Adding {len(items_data.items)} confirmed items to inventory for user {firebase_uid}")
    
    created_or_updated = []
    
    for item_data in items_data.items:
        try:
            # Calculate expiry date if shelf life is provided
            if item_data.estimated_shelf_life_days and item_data.estimated_shelf_life_days > 0:
                item_data.expiry_date = date.today() + timedelta(days=item_data.estimated_shelf_life_days)
            
            # create_inventory_item now handles upsert logic
            item = create_inventory_item(db, firebase_uid, item_data)
            created_or_updated.append(item)
        except Exception as e:
            logger.error(f"Failed to add item {item_data.item_name}: {e}")
            # Continue with other items even if one fails
    
    return {
        "success": True,
        "items_processed": len(created_or_updated),
        "message": f"Successfully processed {len(created_or_updated)} items (new items created or existing quantities updated)"
    }


@router.post(
    "/generate-recipe",
    response_model=RecipeResponse,
    summary="Generate recipe from inventory",
    description="AI generates recipe based on available inventory items"
)
async def generate_recipe(
    filters: RecipeFilters,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate recipe based on user's inventory
    
    - Fetches user's available inventory items
    - Considers dietary preferences
    - Applies filters (cooking time, meal type, cuisine)
    - Generates recipe with available ingredients
    - Shows which ingredients user has vs. needs to buy
    """
    
    logger.info(f"🍳 Generating recipe for user {firebase_uid}")
    
    # Get user's dietary preferences
    user = get_user(db, firebase_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete onboarding first."
        )
    
    # Get user's inventory
    from models.inventory import ItemStatus
    inventory_items = get_user_inventory(
        db,
        firebase_uid,
        status=ItemStatus.ACTIVE,
        limit=500
    )
    
    if not inventory_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No items in inventory. Please add items first before generating recipes."
        )
    
    # Build list of available items
    available_items = [f"{item.item_name} ({item.quantity}{item.unit})" for item in inventory_items]
    
    logger.info(f"Available items: {len(available_items)}")
    
    try:
        # Get Gemini client
        gemini = get_gemini_client()
        
        # Generate recipe
        recipe = await gemini.generate_recipe(
            available_items=available_items,
            dietary_preferences=user.dietary_preferences or {},
            filters=filters.model_dump()
        )
        
        logger.info(f"✅ Generated recipe: {recipe['recipe_name']}")
        
        # Parse and return recipe
        return RecipeResponse(**recipe)
        
    except ValueError as e:
        logger.error(f"Recipe generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating recipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recipe: {str(e)}"
        )


@router.get(
    "/inventory-summary",
    summary="Get inventory summary",
    description="Get summary of user's inventory for recipe generation"
)
async def get_inventory_summary(
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of user's inventory
    Useful for showing what's available before generating recipe
    """
    
    from models.inventory import ItemStatus
    inventory_items = get_user_inventory(
        db,
        firebase_uid,
        status=ItemStatus.ACTIVE,
        limit=500
    )
    
    # Group by category
    categories = {}
    for item in inventory_items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append({
            "name": item.item_name,
            "quantity": float(item.quantity),
            "unit": item.unit
        })
    
    return {
        "total_items": len(inventory_items),
        "categories": categories,
        "summary": f"You have {len(inventory_items)} items in {len(categories)} categories"
    }

