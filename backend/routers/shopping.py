# Shopping list and pattern analysis API endpoints

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from database import get_db
from utils.auth import get_current_user
from schemas.shopping import (
    ShoppingListResponse,
    ShoppingItemResponse,
    PredictionResponse,
    PatternInsightsResponse,
    AnalyzeRequest,
    AnalyzeResponse
)
from crud.pattern_analysis import (
    analyze_and_save_user_patterns,
    get_user_predictions,
    get_shopping_list_grouped,
    get_pattern_insights
)
from models.shopping_prediction import UrgencyLevel, ConfidenceLevel
from utils.pattern_analyzer import generate_shopping_list

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/shopping", tags=["Shopping List & Pattern Analysis"])


@router.get(
    "/list",
    response_model=ShoppingListResponse,
    summary="Get smart shopping list",
    description="Generate AI-powered shopping list based on usage patterns"
)
async def get_shopping_list(
    urgency_filter: Optional[str] = Query(
        None,
        description="Filter by urgency: urgent, this_week, later"
    ),
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get smart shopping list grouped by urgency
    
    The list is generated based on:
    - Purchase frequency patterns
    - Consumption rates
    - Current inventory levels
    - Category-specific buffer times
    
    Items are grouped into:
    - URGENT: Buy today/tomorrow (within category buffer)
    - THIS_WEEK: Buy within 7 days
    - LATER: No immediate rush
    """
    logger.info(f"Generating shopping list for user {firebase_uid}")
    
    try:
        # Generate shopping list using pattern analysis
        shopping_list = generate_shopping_list(
            db=db,
            firebase_uid=firebase_uid,
            urgency_filter=urgency_filter
        )
        
        # Convert to response format
        urgent_items = [ShoppingItemResponse(**item) for item in shopping_list["urgent"]]
        this_week_items = [ShoppingItemResponse(**item) for item in shopping_list["this_week"]]
        later_items = [ShoppingItemResponse(**item) for item in shopping_list["later"]]
        
        total_items = len(urgent_items) + len(this_week_items) + len(later_items)
        
        logger.info(f"Generated shopping list with {total_items} items")
        
        return ShoppingListResponse(
            urgent=urgent_items,
            this_week=this_week_items,
            later=later_items,
            generated_at=datetime.now().isoformat(),
            total_items=total_items
        )
        
    except Exception as e:
        logger.error(f"Error generating shopping list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate shopping list: {str(e)}"
        )


@router.get(
    "/predictions",
    response_model=List[PredictionResponse],
    summary="Get all pattern predictions",
    description="Get stored pattern predictions for all user items"
)
async def get_predictions(
    urgency: Optional[str] = Query(
        None,
        description="Filter by urgency: urgent, this_week, later"
    ),
    min_confidence: Optional[str] = Query(
        None,
        description="Minimum confidence: low, medium, high"
    ),
    limit: int = Query(50, ge=1, le=100),
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pattern predictions for user
    
    Returns stored predictions from last analysis run.
    Use /analyze endpoint to trigger fresh analysis.
    """
    
    # Convert string filters to enums
    urgency_enum = None
    if urgency:
        try:
            urgency_enum = UrgencyLevel(urgency)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid urgency level: {urgency}. Must be: urgent, this_week, later"
            )
    
    confidence_enum = None
    if min_confidence:
        try:
            confidence_enum = ConfidenceLevel(min_confidence)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid confidence level: {min_confidence}. Must be: low, medium, high"
            )
    
    predictions = get_user_predictions(
        db=db,
        firebase_uid=firebase_uid,
        urgency=urgency_enum,
        min_confidence=confidence_enum,
        limit=limit
    )
    
    # Manually serialize to handle datetime fields properly
    result = []
    for pred in predictions:
        pred_dict = {
            "id": pred.id,
            "item_name": pred.item_name,
            "category": pred.category,
            "unit": pred.unit,
            "current_stock": float(pred.current_stock) if pred.current_stock is not None else 0.0,
            "avg_days_between_purchases": float(pred.avg_days_between_purchases) if pred.avg_days_between_purchases else None,
            "avg_quantity_per_purchase": float(pred.avg_quantity_per_purchase) if pred.avg_quantity_per_purchase else None,
            "avg_consumption_rate": float(pred.avg_consumption_rate) if pred.avg_consumption_rate else None,
            "predicted_depletion_date": pred.predicted_depletion_date.isoformat() if pred.predicted_depletion_date else None,
            "days_until_depletion": float(pred.days_until_depletion) if pred.days_until_depletion is not None else None,
            "suggested_quantity": float(pred.suggested_quantity) if pred.suggested_quantity else None,
            "confidence_level": pred.confidence_level.value if hasattr(pred.confidence_level, 'value') else str(pred.confidence_level),
            "urgency": pred.urgency.value if hasattr(pred.urgency, 'value') else str(pred.urgency),
            "data_points_count": pred.data_points_count,
            "last_analyzed": pred.last_analyzed.isoformat() if pred.last_analyzed else None
        }
        result.append(pred_dict)
    
    return result


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Trigger pattern analysis",
    description="Manually trigger pattern analysis for all user items"
)
async def trigger_analysis(
    request: AnalyzeRequest = AnalyzeRequest(),
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger pattern analysis and save predictions
    
    This endpoint allows users to manually trigger analysis.
    Normally, analysis runs automatically via background job at 6 AM IST.
    
    Use force_refresh=true to re-analyze even if recent analysis exists.
    """
    logger.info(f"Manual analysis triggered for user {firebase_uid}")
    
    try:
        # Run pattern analysis and save predictions
        predictions_saved = analyze_and_save_user_patterns(
            db=db,
            firebase_uid=firebase_uid
        )
        
        return AnalyzeResponse(
            message="Pattern analysis completed successfully",
            items_analyzed=predictions_saved,
            predictions_saved=predictions_saved
        )
        
    except Exception as e:
        logger.error(f"Analysis failed for user {firebase_uid}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern analysis failed: {str(e)}"
        )


@router.get(
    "/insights/{item_name}",
    response_model=PatternInsightsResponse,
    summary="Get item pattern insights",
    description="Get detailed pattern insights for a specific item"
)
async def get_item_insights(
    item_name: str,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed pattern insights for a specific item
    
    Shows:
    - Purchase frequency patterns
    - Consumption rates
    - Predicted depletion date
    - Smart suggestions
    - Confidence levels
    """
    insights = get_pattern_insights(
        db=db,
        firebase_uid=firebase_uid,
        item_name=item_name
    )
    
    if not insights:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No pattern data found for item: {item_name}. Add the item to inventory and track usage to generate insights."
        )
    
    return insights


@router.get(
    "/health",
    summary="Check pattern analysis system health",
    description="Verify pattern analysis system is working"
)
async def health_check(
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Health check for pattern analysis system
    
    Returns basic statistics about user's pattern data
    """
    from models.purchase_log import PurchaseLog
    from models.consumption_log import ConsumptionLog
    from models.shopping_prediction import ShoppingPrediction
    
    # Count data points
    purchase_count = db.query(PurchaseLog).filter(
        PurchaseLog.firebase_uid == firebase_uid
    ).count()
    
    consumption_count = db.query(ConsumptionLog).filter(
        ConsumptionLog.firebase_uid == firebase_uid
    ).count()
    
    prediction_count = db.query(ShoppingPrediction).filter(
        ShoppingPrediction.firebase_uid == firebase_uid
    ).count()
    
    return {
        "status": "healthy",
        "user_id": firebase_uid,
        "data_points": {
            "purchases_logged": purchase_count,
            "consumptions_logged": consumption_count,
            "predictions_generated": prediction_count
        },
        "ready_for_analysis": purchase_count >= 3 or consumption_count >= 3,
        "message": "Pattern analysis system is operational"
    }
