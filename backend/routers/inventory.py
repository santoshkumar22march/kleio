# Inventory management endpoints


from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from utils.auth import get_current_user
from schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    InventoryMarkUsed,
    BulkInventoryCreate
)
from crud.inventory import (
    create_inventory_item,
    get_user_inventory,
    get_inventory_item,
    update_inventory_item,
    delete_inventory_item,
    mark_item_as_used,
    get_common_items
)
from models.inventory import ItemStatus

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.post(
    "/add",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add inventory item",
    description="Add a new item to household inventory manually"
)
async def add_item(
    item_data: InventoryCreate,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new inventory item
    
    - **item_name**: Name of the item (e.g., "Tomatoes")
    - **category**: Category (vegetables, fruits, dairy, staples, etc.)
    - **quantity**: Quantity amount
    - **unit**: Unit of measurement (kg, liters, pieces, etc.)
    - **expiry_date**: Optional expiry date
    """
    item = create_inventory_item(db, firebase_uid, item_data)
    return item


@router.post(
    "/bulk-add",
    response_model=List[InventoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add multiple items",
    description="Add multiple inventory items at once (used for photo-based addition)"
)
async def bulk_add_items(
    bulk_data: BulkInventoryCreate,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Add multiple inventory items at once

    created_items = []
    
    for item_data in bulk_data.items:
        item = create_inventory_item(db, firebase_uid, item_data)
        created_items.append(item)
    
    return created_items


@router.get(
    "/list",
    response_model=List[InventoryResponse],
    summary="List inventory items",
    description="Get user's inventory items with optional filters"
)
async def list_items(
    status_filter: Optional[str] = Query(None, description="Filter by status (active, consumed, expired)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=500, description="Maximum items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    # Get user's inventory items
    
    """
    Supports filtering by:
    - **status**: active, consumed, expired, discarded
    - **category**: vegetables, fruits, dairy, etc.
    - **limit**: Max items to return (pagination)
    - **offset**: Items to skip (pagination)
    """
    # Convert status string to enum
    status_enum = None
    if status_filter:
        try:
            status_enum = ItemStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in ItemStatus]}"
            )
    
    items = get_user_inventory(db, firebase_uid, status_enum, category, limit, offset)
    return items


@router.get(
    "/{item_id}",
    response_model=InventoryResponse,
    summary="Get inventory item",
    description="Get a specific inventory item by ID"
)
async def get_item(
    item_id: int,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get a specific inventory item

    item = get_inventory_item(db, item_id, firebase_uid)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item


@router.patch(
    "/{item_id}/update",
    response_model=InventoryResponse,
    summary="Update inventory item",
    description="Update quantity, expiry date, or status of an item"
)
async def update_item(
    item_id: int,
    update_data: InventoryUpdate,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update an inventory item

    item = update_inventory_item(db, item_id, firebase_uid, update_data)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete inventory item",
    description="Soft delete an inventory item (marks as consumed)"
)
async def delete_item(
    item_id: int,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete (soft delete) an inventory item

    success = delete_inventory_item(db, item_id, firebase_uid)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return None


@router.post(
    "/{item_id}/mark-used",
    response_model=InventoryResponse,
    summary="Mark item as used",
    description="Mark item as consumed and log for pattern analysis"
)
async def mark_used(
    item_id: int,
    used_data: InventoryMarkUsed,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark item as used/consumed
    
    Logs consumption for pattern analysis and shopping list predictions.
    Can mark partial consumption or full consumption.
    """
    item = mark_item_as_used(db, item_id, firebase_uid, used_data)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get item categories",
    description="Get list of common item categories for autocomplete"
)
async def get_categories():
    """Get list of common item categories"""
    return [
        "vegetables",
        "fruits",
        "dairy",
        "staples",
        "spices",
        "snacks",
        "beverages",
        "meat",
        "seafood",
        "bakery",
        "frozen",
        "condiments",
        "pulses",
        "oils",
        "others"
    ]


@router.get(
    "/units",
    response_model=List[str],
    summary="Get units",
    description="Get list of common units for autocomplete"
)
async def get_units():
    """Get list of common units of measurement"""
    return [
        "kg",
        "grams",
        "liters",
        "ml",
        "pieces",
        "dozens",
        "packets",
        "bottles",
        "cans",
        "bunches"
    ]


@router.get(
    "/common-items",
    response_model=List[str],
    summary="Get common items",
    description="Get autocomplete suggestions for item names"
)
async def get_common_item_suggestions(
    q: Optional[str] = Query(None, description="Search query"),
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get autocomplete suggestions for item names

    # Based on user's past items + common Indian groceries
    
    user_items = get_common_items(db, firebase_uid, q, limit=5)
    
    # Add common Indian grocery items
    common_items = [
        "Rice", "Wheat Flour (Atta)", "Dal (Lentils)", "Tomatoes", "Onions",
        "Potatoes", "Milk", "Yogurt (Curd)", "Paneer", "Ghee",
        "Oil", "Sugar", "Salt", "Tea", "Coffee",
        "Turmeric", "Red Chili Powder", "Coriander Powder", "Cumin Seeds",
        "Garam Masala", "Bread", "Eggs", "Chicken", "Mutton"
    ]
    
    # Filter common items by query if provided
    if q:
        common_items = [item for item in common_items if q.lower() in item.lower()]
    
    # Combine and remove duplicates
    all_items = list(set(user_items + common_items[:10]))
    
    return all_items[:15]

