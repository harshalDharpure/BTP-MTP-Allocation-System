"""
Test script for the BTP/MTP Allocation Engine
"""

import pandas as pd
import logging
from allocation_engine import AllocationEngine
import os

# Configure logging for testing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_allocation_engine():
    """Test the allocation engine with sample data"""
    
    try:
        logger.info("Starting allocation engine test...")
        
        # Initialize engine
        engine = AllocationEngine()
        
        # Check if input file exists
        input_file = 'input_btp_mtp_allocation.csv'
        if not os.path.exists(input_file):
            logger.error(f"Input file {input_file} not found!")
            return False
        
        # Load data
        if not engine.load_data(input_file):
            logger.error("Failed to load data")
            return False
        
        # Perform allocation
        allocation_results = engine.allocate_students()
        logger.info(f"Allocation completed for {len(allocation_results)} students")
        
        # Generate preference statistics
        preference_stats = engine.generate_preference_stats()
        logger.info(f"Preference statistics generated for {len(preference_stats)} faculties")
        
        # Get summary
        summary = engine.get_allocation_summary()
        logger.info(f"Allocation summary: {summary}")
        
        # Save results
        engine.save_allocation_results('test_allocation_output.csv')
        engine.save_preference_stats('test_preference_stats.csv')
        
        logger.info("✅ Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

def validate_results():
    """Validate the allocation results"""
    
    try:
        # Load results
        allocation_df = pd.read_csv('test_allocation_output.csv')
        preference_df = pd.read_csv('test_preference_stats.csv')
        
        logger.info("=== VALIDATION RESULTS ===")
        logger.info(f"Total students allocated: {len(allocation_df)}")
        logger.info(f"Unique faculties: {allocation_df['Allocated'].nunique()}")
        logger.info(f"Faculty distribution:")
        
        faculty_dist = allocation_df['Allocated'].value_counts()
        for faculty, count in faculty_dist.items():
            logger.info(f"  {faculty}: {count} students")
        
        # Check for any unallocated students
        unallocated = allocation_df[allocation_df['Allocated'].isna()]
        if len(unallocated) > 0:
            logger.warning(f"⚠️  {len(unallocated)} students not allocated!")
        else:
            logger.info("✅ All students allocated successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🧪 Running BTP/MTP Allocation Engine Tests")
    logger.info("=" * 50)
    
    # Run tests
    test_success = test_allocation_engine()
    
    if test_success:
        validate_results()
        logger.info("🎉 All tests passed!")
    else:
        logger.error("💥 Tests failed!")
