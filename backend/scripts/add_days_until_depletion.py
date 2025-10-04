# Migration script to add days_until_depletion column to shopping_predictions table
# Run this once to update the database schema

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables before importing anything else
from dotenv import load_dotenv
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(backend_dir, '.env')
load_dotenv(env_file)

from database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_days_until_depletion_column():
    """Add days_until_depletion column to shopping_predictions table"""
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'shopping_predictions' 
                AND column_name = 'days_until_depletion'
            """)
            result = conn.execute(check_query)
            
            if result.fetchone():
                logger.info("✅ Column 'days_until_depletion' already exists. No migration needed.")
                return
            
            # Add the column
            alter_query = text("""
                ALTER TABLE shopping_predictions 
                ADD COLUMN days_until_depletion FLOAT
            """)
            
            conn.execute(alter_query)
            conn.commit()
            
            logger.info("✅ Successfully added 'days_until_depletion' column to shopping_predictions table")
            logger.info("💡 Now re-run pattern analysis to populate the new field:")
            logger.info("   POST /api/shopping/analyze")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    logger.info("🔧 Starting database migration...")
    add_days_until_depletion_column()
    logger.info("🎉 Migration complete!")

