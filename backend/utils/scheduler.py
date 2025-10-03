# Background job scheduler for pattern analysis
# Runs daily pattern analysis for all active users at 6 AM IST

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import pytz

from database import SessionLocal
from crud.pattern_analysis import analyze_and_save_user_patterns, delete_old_predictions
from models.user import User

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()

# IST timezone
IST = pytz.timezone('Asia/Kolkata')


def run_daily_pattern_analysis():
    """
    Run pattern analysis for all active users
    
    This job:
    1. Gets all users from database
    2. Analyzes consumption and purchase patterns for each user
    3. Saves/updates predictions in shopping_predictions table
    4. Cleans up old predictions (items not purchased in 90 days)
    
    Runs daily at 6:00 AM IST (as per PRD requirement)
    """
    logger.info("🔄 Starting daily pattern analysis job...")
    
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users for pattern analysis")
        
        total_predictions = 0
        successful_users = 0
        failed_users = 0
        
        for user in users:
            try:
                # Analyze patterns for this user
                predictions_saved = analyze_and_save_user_patterns(
                    db=db,
                    firebase_uid=user.firebase_uid
                )
                
                # Clean up old predictions
                deleted = delete_old_predictions(
                    db=db,
                    firebase_uid=user.firebase_uid
                )
                
                total_predictions += predictions_saved
                successful_users += 1
                
                logger.info(f"✅ User {user.firebase_uid}: {predictions_saved} predictions saved, {deleted} old predictions cleaned")
                
            except Exception as e:
                failed_users += 1
                logger.error(f"❌ Failed to analyze patterns for user {user.firebase_uid}: {e}")
        
        logger.info(f"""
        ✅ Daily pattern analysis completed!
        - Users processed: {successful_users}
        - Failed: {failed_users}
        - Total predictions: {total_predictions}
        """)
        
    except Exception as e:
        logger.error(f"❌ Daily pattern analysis job failed: {e}")
    
    finally:
        db.close()


def start_scheduler():
    """
    Start the background job scheduler
    
    Jobs:
    - Daily pattern analysis: 6:00 AM IST every day
    """
    
    # Add daily pattern analysis job
    scheduler.add_job(
        run_daily_pattern_analysis,
        trigger=CronTrigger(
            hour=6,      # 6 AM
            minute=0,    # At :00
            timezone=IST
        ),
        id='daily_pattern_analysis',
        name='Daily Pattern Analysis',
        replace_existing=True,
        max_instances=1  # Only one instance at a time
    )
    
    # Start the scheduler
    scheduler.start()
    
    logger.info("✅ Background job scheduler started")
    logger.info("📅 Daily pattern analysis scheduled for 6:00 AM IST")
    
    # Log next run time
    job = scheduler.get_job('daily_pattern_analysis')
    if job:
        next_run = job.next_run_time
        logger.info(f"⏰ Next pattern analysis run: {next_run}")


def stop_scheduler():
    """Stop the background job scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Background job scheduler stopped")


def trigger_immediate_analysis():
    """
    Trigger pattern analysis immediately (for testing/manual trigger)
    
    This can be called from an admin endpoint or for testing purposes
    """
    logger.info("▶️ Triggering immediate pattern analysis...")
    run_daily_pattern_analysis()


# For manual testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Running pattern analysis manually...")
    run_daily_pattern_analysis()
