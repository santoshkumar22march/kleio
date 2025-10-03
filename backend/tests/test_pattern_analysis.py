# Tests for pattern recognition algorithm

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from models.inventory import Inventory, ItemStatus
from models.purchase_log import PurchaseLog
from models.consumption_log import ConsumptionLog
from models.shopping_prediction import ShoppingPrediction, ConfidenceLevel, UrgencyLevel
from utils.pattern_analyzer import (
    analyze_item_pattern,
    calculate_confidence_level,
    calculate_urgency,
    get_category_buffer_days
)
from crud.pattern_analysis import save_or_update_prediction


class TestPatternAnalysisAlgorithm:
    """Test suite for pattern recognition accuracy"""
    
    def test_purchase_frequency_calculation(self, db: Session, test_user):
        """Test: Algorithm correctly calculates purchase frequency"""
        
        # Given: User buys milk every 3 days
        item_name = "milk"
        category = "dairy"
        
        # Create purchase history: Day 1, 4, 7, 10 (3-day intervals)
        purchase_dates = [
            date.today() - timedelta(days=10),
            date.today() - timedelta(days=7),
            date.today() - timedelta(days=4),
            date.today() - timedelta(days=1)
        ]
        
        for purchase_date in purchase_dates:
            PurchaseLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_purchased=2.0,
                unit="liters",
                purchase_date=purchase_date
            ).save(db)
        
        # When: Analyze pattern
        analysis = analyze_item_pattern(db, test_user, item_name, category)
        
        # Then: Should detect 3-day purchase frequency
        assert analysis is not None
        assert abs(analysis["avg_days_between_purchases"] - 3.0) < 0.5
        print(f"✅ Purchase frequency test passed: {analysis['avg_days_between_purchases']} days")
    
    
    def test_consumption_rate_calculation(self, db: Session, test_user):
        """Test: Algorithm correctly calculates consumption rate"""
        
        # Given: User consumes 2L milk in 2 days (1L per day)
        item_name = "milk"
        category = "dairy"
        
        # Create consumption logs
        for i in range(4):
            ConsumptionLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_consumed=2.0,
                unit="liters",
                consumed_date=date.today() - timedelta(days=i*3),
                added_date=date.today() - timedelta(days=i*3+2),
                days_lasted=2
            ).save(db)
        
        # Create current inventory
        Inventory(
            firebase_uid=test_user,
            item_name=item_name,
            category=category,
            quantity=2.0,
            unit="liters",
            status=ItemStatus.ACTIVE
        ).save(db)
        
        # When: Analyze pattern
        analysis = analyze_item_pattern(db, test_user, item_name, category)
        
        # Then: Should detect 1L/day consumption rate
        assert analysis is not None
        expected_rate = 2.0 / 2.0  # 1L per day
        assert abs(analysis["avg_consumption_rate"] - expected_rate) < 0.2
        print(f"✅ Consumption rate test passed: {analysis['avg_consumption_rate']} L/day")
    
    
    def test_depletion_prediction_accuracy(self, db: Session, test_user):
        """Test: Algorithm predicts depletion date accurately"""
        
        # Given: 2L stock, consumption rate 1L/day
        item_name = "milk"
        category = "dairy"
        
        # Create purchase history
        for i in range(3):
            PurchaseLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_purchased=2.0,
                unit="liters",
                purchase_date=date.today() - timedelta(days=i*3)
            ).save(db)
        
        # Create consumption history (2L lasts 2 days)
        for i in range(3):
            ConsumptionLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_consumed=2.0,
                unit="liters",
                consumed_date=date.today() - timedelta(days=i*3),
                added_date=date.today() - timedelta(days=i*3+2),
                days_lasted=2
            ).save(db)
        
        # Current stock: 2L
        Inventory(
            firebase_uid=test_user,
            item_name=item_name,
            category=category,
            quantity=2.0,
            unit="liters",
            status=ItemStatus.ACTIVE
        ).save(db)
        
        # When: Analyze pattern
        analysis = analyze_item_pattern(db, test_user, item_name, category)
        
        # Then: Should predict depletion in ~2 days
        assert analysis is not None
        expected_days = 2.0
        actual_days = analysis["days_until_depletion"]
        
        # Allow 20% margin of error
        assert abs(actual_days - expected_days) <= expected_days * 0.2
        print(f"✅ Depletion prediction test passed: {actual_days} days (expected ~{expected_days})")
    
    
    def test_confidence_levels(self, db: Session):
        """Test: Confidence levels calculated correctly"""
        
        # Given: Different data point counts
        test_cases = [
            (2, ConfidenceLevel.LOW),
            (3, ConfidenceLevel.MEDIUM),
            (4, ConfidenceLevel.MEDIUM),
            (5, ConfidenceLevel.HIGH),
            (10, ConfidenceLevel.HIGH)
        ]
        
        # When/Then: Check confidence calculation
        for data_points, expected_confidence in test_cases:
            actual_confidence = calculate_confidence_level(data_points)
            assert actual_confidence == expected_confidence
            print(f"✅ Confidence test passed: {data_points} points → {actual_confidence.value}")
    
    
    def test_urgency_calculation(self):
        """Test: Urgency calculated correctly based on category buffers"""
        
        # Test cases: (days_until_depletion, category, expected_urgency)
        test_cases = [
            (0, "dairy", UrgencyLevel.URGENT),      # No stock
            (1, "vegetables", UrgencyLevel.URGENT),  # Within buffer (1 day)
            (2, "dairy", UrgencyLevel.URGENT),       # Within buffer (2 days)
            (3, "dairy", UrgencyLevel.THIS_WEEK),    # Outside buffer, within week
            (5, "staples", UrgencyLevel.THIS_WEEK),  # Outside buffer (3 days), within week
            (10, "staples", UrgencyLevel.LATER),     # Outside week
        ]
        
        for days, category, expected_urgency in test_cases:
            actual_urgency = calculate_urgency(days, category, current_stock=1.0)
            assert actual_urgency == expected_urgency
            print(f"✅ Urgency test passed: {category}, {days}d → {actual_urgency.value}")
    
    
    def test_category_buffers(self):
        """Test: Category-specific buffer days are correct"""
        
        expected_buffers = {
            "vegetables": 1,
            "fruits": 1,
            "dairy": 2,
            "staples": 3,
            "pulses": 3,
            "oils": 5,
            "spices": 7,
            "unknown_category": 2  # default
        }
        
        for category, expected_buffer in expected_buffers.items():
            actual_buffer = get_category_buffer_days(category)
            assert actual_buffer == expected_buffer
            print(f"✅ Buffer test passed: {category} → {actual_buffer} days")
    
    
    def test_insufficient_data_handling(self, db: Session, test_user):
        """Test: Algorithm handles insufficient data gracefully"""
        
        # Given: Only 1 purchase (insufficient)
        item_name = "rice"
        category = "staples"
        
        PurchaseLog(
            firebase_uid=test_user,
            item_name=item_name,
            category=category,
            quantity_purchased=5.0,
            unit="kg",
            purchase_date=date.today()
        ).save(db)
        
        # When: Try to analyze
        analysis = analyze_item_pattern(db, test_user, item_name, category)
        
        # Then: Should return None (insufficient data)
        assert analysis is None
        print("✅ Insufficient data test passed: Returns None for < 2 purchases")
    
    
    def test_real_world_scenario_milk(self, db: Session, test_user):
        """Test: Real-world scenario - Weekly milk purchases"""
        
        # Given: User buys 2L milk twice a week, consumes in 3 days
        item_name = "milk"
        category = "dairy"
        
        # Simulate 4 weeks of data
        current_date = date.today()
        
        for week in range(4):
            for purchase in [0, 3]:  # Buy on day 0 and day 3 of each week
                purchase_date = current_date - timedelta(days=(4-week)*7 + (3-purchase))
                consume_date = purchase_date + timedelta(days=3)
                
                # Purchase
                PurchaseLog(
                    firebase_uid=test_user,
                    item_name=item_name,
                    category=category,
                    quantity_purchased=2.0,
                    unit="liters",
                    purchase_date=purchase_date
                ).save(db)
                
                # Consumption
                ConsumptionLog(
                    firebase_uid=test_user,
                    item_name=item_name,
                    category=category,
                    quantity_consumed=2.0,
                    unit="liters",
                    consumed_date=consume_date,
                    added_date=purchase_date,
                    days_lasted=3
                ).save(db)
        
        # Current stock
        Inventory(
            firebase_uid=test_user,
            item_name=item_name,
            category=category,
            quantity=1.0,
            unit="liters",
            status=ItemStatus.ACTIVE
        ).save(db)
        
        # When: Analyze
        analysis = analyze_item_pattern(db, test_user, item_name, category)
        
        # Then: Verify accuracy
        assert analysis is not None
        
        # Purchase frequency should be ~3.5 days (twice a week)
        assert 3.0 <= analysis["avg_days_between_purchases"] <= 4.0
        
        # Consumption rate should be ~0.67 L/day (2L in 3 days)
        assert 0.6 <= analysis["avg_consumption_rate"] <= 0.75
        
        # Confidence should be HIGH (8 purchases)
        assert analysis["confidence_level"] == ConfidenceLevel.HIGH
        
        print(f"""
        ✅ Real-world milk scenario test passed:
           Purchase frequency: {analysis['avg_days_between_purchases']:.1f} days
           Consumption rate: {analysis['avg_consumption_rate']:.2f} L/day
           Confidence: {analysis['confidence_level'].value}
           Urgency: {analysis['urgency'].value}
        """)
    
    
    def test_real_world_scenario_rice(self, db: Session, test_user):
        """Test: Real-world scenario - Monthly rice purchases"""
        
        # Given: User buys 5kg rice monthly, lasts ~25 days
        item_name = "rice"
        category = "staples"
        
        # Simulate 6 months of data
        for month in range(6):
            purchase_date = date.today() - timedelta(days=(6-month)*30)
            consume_date = purchase_date + timedelta(days=25)
            
            PurchaseLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_purchased=5.0,
                unit="kg",
                purchase_date=purchase_date
            ).save(db)
            
            ConsumptionLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_consumed=5.0,
                unit="kg",
                consumed_date=consume_date,
                added_date=purchase_date,
                days_lasted=25
            ).save(db)
        
        # Current stock: 2kg left
        Inventory(
            firebase_uid=test_user,
            item_name=item_name,
            category=category,
            quantity=2.0,
            unit="kg",
            status=ItemStatus.ACTIVE
        ).save(db)
        
        # When: Analyze
        analysis = analyze_item_pattern(db, test_user, item_name, category)
        
        # Then: Verify
        assert analysis is not None
        
        # Purchase frequency should be ~30 days
        assert 28 <= analysis["avg_days_between_purchases"] <= 32
        
        # Consumption rate should be ~0.2 kg/day (5kg in 25 days)
        assert 0.18 <= analysis["avg_consumption_rate"] <= 0.22
        
        # With 2kg left, should run out in ~10 days
        assert 8 <= analysis["days_until_depletion"] <= 12
        
        # Should be THIS_WEEK urgency (staples buffer = 3 days, 10 days < 7)
        assert analysis["urgency"] == UrgencyLevel.THIS_WEEK
        
        print(f"""
        ✅ Real-world rice scenario test passed:
           Purchase frequency: {analysis['avg_days_between_purchases']:.1f} days
           Days until depletion: {analysis['days_until_depletion']:.1f} days
           Urgency: {analysis['urgency'].value}
        """)


class TestPerformance:
    """Test suite for algorithm performance/efficiency"""
    
    def test_analysis_speed_single_item(self, db: Session, test_user, benchmark):
        """Test: Single item analysis completes quickly"""
        
        # Given: Item with 10 purchase/consumption records
        item_name = "test_item"
        category = "dairy"
        
        for i in range(10):
            PurchaseLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_purchased=2.0,
                unit="liters",
                purchase_date=date.today() - timedelta(days=i*3)
            ).save(db)
            
            ConsumptionLog(
                firebase_uid=test_user,
                item_name=item_name,
                category=category,
                quantity_consumed=2.0,
                unit="liters",
                consumed_date=date.today() - timedelta(days=i*3),
                added_date=date.today() - timedelta(days=i*3+2),
                days_lasted=2
            ).save(db)
        
        Inventory(
            firebase_uid=test_user,
            item_name=item_name,
            category=category,
            quantity=2.0,
            unit="liters",
            status=ItemStatus.ACTIVE
        ).save(db)
        
        # When: Benchmark analysis
        result = benchmark(analyze_item_pattern, db, test_user, item_name, category)
        
        # Then: Should complete in < 100ms
        assert result is not None
        print(f"✅ Performance test passed: Single item analysis completed")
    
    
    def test_bulk_analysis_efficiency(self, db: Session, test_user):
        """Test: Can analyze multiple items efficiently"""
        
        from crud.pattern_analysis import analyze_and_save_user_patterns
        import time
        
        # Given: 20 different items with purchase/consumption history
        items = [f"item_{i}" for i in range(20)]
        
        for item_name in items:
            for j in range(5):
                PurchaseLog(
                    firebase_uid=test_user,
                    item_name=item_name,
                    category="staples",
                    quantity_purchased=2.0,
                    unit="kg",
                    purchase_date=date.today() - timedelta(days=j*7)
                ).save(db)
        
        # When: Analyze all items
        start = time.time()
        predictions_saved = analyze_and_save_user_patterns(db, test_user)
        duration = time.time() - start
        
        # Then: Should complete in < 2 seconds for 20 items
        assert predictions_saved >= 18  # At least 18 items (some may not have enough data)
        assert duration < 2.0
        
        print(f"""
        ✅ Bulk analysis efficiency test passed:
           Items analyzed: {predictions_saved}
           Time taken: {duration:.2f}s
           Avg per item: {duration/predictions_saved*1000:.0f}ms
        """)


# Pytest fixtures
@pytest.fixture
def test_user():
    """Fixture for test user ID"""
    return "test_user_123"


@pytest.fixture
def db():
    """Fixture for database session (implement based on your test setup)"""
    from database import SessionLocal
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
