import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_time_dimension():
    """Test that time dimension meets all requirements"""
    
    print("Testing Time Dimension...")
    
    # Load the generated data
    df = pd.read_csv('generated_data/time_dimension.csv')
    
    # Test 1: Required columns
    required_columns = ['Time Key', 'Time Description']
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"
    print("✓ All required columns present")
    
    # Test 2: Record count (3 years of weekly data = ~156 weeks)
    expected_weeks = 156  # 52 weeks * 3 years
    tolerance = 4  # Allow for partial years
    assert expected_weeks - tolerance <= len(df) <= expected_weeks + tolerance, \
        f"Expected ~{expected_weeks} weeks, got {len(df)}"
    print(f"✓ Record count: {len(df)} weeks (3 years of data)")
    
    # Test 3: Time Key uniqueness
    assert df['Time Key'].nunique() == len(df), "Time Keys are not unique"
    print("✓ Time Keys are unique")
    
    # Test 4: Time Key sequence
    # Check if Time Keys are sequential
    time_keys = df['Time Key'].sort_values().values
    differences = np.diff(time_keys)
    assert all(d == 1 for d in differences), "Time Keys should be sequential"
    print("✓ Time Keys are sequential")
    
    # Test 5: Time Description format
    # Expected format: "1 w/e DD Mon, YYYY"
    sample_descriptions = df['Time Description'].head(10)
    
    for desc in sample_descriptions:
        # Check for "w/e" pattern
        assert 'w/e' in desc.lower(), f"Time description missing 'w/e': {desc}"
        
        # Check for year (should be 2022-2025)
        years = ['2022', '2023', '2024', '2025']
        has_year = any(year in desc for year in years)
        assert has_year, f"Time description missing valid year: {desc}"
    
    print("✓ Time descriptions follow expected format")
    
    # Test 6: Date range validation
    # Extract years from descriptions
    years_in_data = set()
    for desc in df['Time Description']:
        for year in ['2022', '2023', '2024', '2025']:
            if year in desc:
                years_in_data.add(year)
    
    assert len(years_in_data) >= 3, f"Should cover at least 3 years, found: {years_in_data}"
    print(f"✓ Years covered: {sorted(years_in_data)}")
    
    # Test 7: Weekly periods
    # Check that descriptions indicate weekly periods
    weekly_indicators = ['w/e', 'week ending', 'w.e.']
    has_weekly = df['Time Description'].str.contains('|'.join(weekly_indicators), case=False, na=False).all()
    assert has_weekly, "All time descriptions should indicate weekly periods"
    print("✓ All periods are weekly")
    
    # Test 8: Month coverage
    # Check that all months are represented
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    months_found = set()
    for month in months:
        if df['Time Description'].str.contains(month, case=False, na=False).any():
            months_found.add(month)
    
    assert len(months_found) == 12, f"Should cover all 12 months, found: {months_found}"
    print("✓ All 12 months represented")
    
    # Test 9: Check for key holiday weeks
    # Christmas week (late December)
    christmas_weeks = df['Time Description'].str.contains('Dec', case=False, na=False)
    christmas_count = christmas_weeks.sum()
    assert christmas_count >= 9, f"Should have at least 9 December weeks (3 years), found {christmas_count}"
    
    # Easter period (March/April)
    easter_months = df['Time Description'].str.contains('Mar|Apr', case=False, na=False)
    easter_count = easter_months.sum()
    assert easter_count >= 18, f"Should have March/April weeks for Easter period, found {easter_count}"
    
    print("✓ Key holiday periods covered (Christmas, Easter)")
    
    # Test 10: No duplicate Time Descriptions
    assert df['Time Description'].nunique() == len(df), "Time descriptions should be unique"
    print("✓ All time descriptions are unique")
    
    # Test 11: Consistent week endings
    # Most retail weeks end on Saturday or Sunday
    if 'Sat' in df['Time Description'].iloc[0] or 'Sun' in df['Time Description'].iloc[0]:
        print("✓ Week endings appear consistent")
    
    # Test 12: Time Key starting range
    # Should start around 2201 based on requirements
    min_key = df['Time Key'].min()
    assert 2000 <= min_key <= 2500, f"Time Key should start around 2201, got {min_key}"
    print(f"✓ Time Key starts at: {min_key}")
    
    # Test 13: Summer period coverage
    summer_months = df['Time Description'].str.contains('Jun|Jul|Aug', case=False, na=False)
    summer_count = summer_months.sum()
    assert summer_count >= 27, f"Should have summer weeks (Jun-Aug), found {summer_count}"
    print("✓ Summer period covered")
    
    # Test 14: Valentine's period (February)
    valentine_weeks = df['Time Description'].str.contains('Feb', case=False, na=False)
    valentine_count = valentine_weeks.sum()
    assert valentine_count >= 9, f"Should have February weeks for Valentine's, found {valentine_count}"
    print("✓ Valentine's period covered")
    
    print("\n✅ All Time Dimension tests passed!")
    return True

if __name__ == "__main__":
    test_time_dimension()