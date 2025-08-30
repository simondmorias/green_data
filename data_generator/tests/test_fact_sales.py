import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fact_sales():
    """Test that fact sales table meets all requirements"""
    
    print("Testing Fact Sales Table...")
    
    # Load the generated data
    df = pd.read_csv('generated_data/fact_sales.csv')
    
    # Test 1: Column count
    expected_columns = 188
    tolerance = 10  # Allow some flexibility
    assert expected_columns - tolerance <= len(df.columns) <= expected_columns + tolerance, \
        f"Expected ~{expected_columns} columns, got {len(df.columns)}"
    print(f"✓ Column count: {len(df.columns)} (expected ~188)")
    
    # Test 2: Key columns exist
    key_columns = ['Geography Key', 'Product Key', 'Time Key']
    for col in key_columns:
        assert col in df.columns, f"Missing key column: {col}"
    print("✓ All key columns present")
    
    # Test 3: Core sales metrics exist
    core_metrics = ['Unit Sales', 'Volume Sales', 'Value Sales']
    for metric in core_metrics:
        assert metric in df.columns, f"Missing core metric: {metric}"
    print("✓ Core sales metrics present")
    
    # Test 4: Sparsity check (~40% of combinations should have sales)
    total_possible = len(df)
    non_null_sales = df['Value Sales'].notna().sum()
    sparsity_rate = non_null_sales / total_possible if total_possible > 0 else 0
    
    assert 0.30 <= sparsity_rate <= 0.50, \
        f"Expected ~40% of combinations to have sales, got {sparsity_rate:.1%}"
    print(f"✓ Sparsity rate: {sparsity_rate:.1%} (target ~40%)")
    
    # Test 5: Foreign key integrity
    # Load dimension tables to check
    products_df = pd.read_csv('generated_data/products_dimension.csv')
    geography_df = pd.read_csv('generated_data/geography_dimension.csv')
    time_df = pd.read_csv('generated_data/time_dimension.csv')
    
    # Check Product Keys
    invalid_products = ~df['Product Key'].isin(products_df['Product Key'])
    assert invalid_products.sum() == 0, f"Found {invalid_products.sum()} invalid Product Keys"
    
    # Check Geography Keys
    invalid_geographies = ~df['Geography Key'].isin(geography_df['Geography Key'])
    assert invalid_geographies.sum() == 0, f"Found {invalid_geographies.sum()} invalid Geography Keys"
    
    # Check Time Keys
    invalid_times = ~df['Time Key'].isin(time_df['Time Key'])
    assert invalid_times.sum() == 0, f"Found {invalid_times.sum()} invalid Time Keys"
    
    print("✓ All foreign keys valid")
    
    # Test 6: Value = Volume × Price relationship
    # Sample check on non-null rows
    valid_sales = df[(df['Value Sales'].notna()) & (df['Volume Sales'].notna()) & (df['Unit Sales'].notna())].head(100)
    
    if len(valid_sales) > 0:
        # Calculate implied price per unit
        implied_price = valid_sales['Value Sales'] / valid_sales['Volume Sales']
        
        # Check that prices are reasonable (£0.01 to £100 per unit volume)
        reasonable_prices = (implied_price >= 0.01) & (implied_price <= 100)
        assert reasonable_prices.mean() > 0.90, "Price per volume should be reasonable"
        print("✓ Value/Volume price relationships validated")
    
    # Test 7: Base vs Total sales relationship
    if 'Base Unit Sales' in df.columns and 'Unit Sales' in df.columns:
        # Base sales should be <= Total sales
        valid_base = df[(df['Base Unit Sales'].notna()) & (df['Unit Sales'].notna())]
        if len(valid_base) > 0:
            assert (valid_base['Base Unit Sales'] <= valid_base['Unit Sales']).all(), \
                "Base sales should not exceed total sales"
            print("✓ Base sales <= Total sales")
    
    # Test 8: Promotional metrics
    promo_columns = [col for col in df.columns if 'Promo' in col or 'Discount' in col]
    if len(promo_columns) > 0:
        print(f"✓ Promotional columns found: {len(promo_columns)}")
        
        # Check that promotional sales don't exceed total sales
        if 'Total Promo Unit Sales' in df.columns and 'Unit Sales' in df.columns:
            valid_promo = df[(df['Total Promo Unit Sales'].notna()) & (df['Unit Sales'].notna())]
            if len(valid_promo) > 0:
                assert (valid_promo['Total Promo Unit Sales'] <= valid_promo['Unit Sales']).all(), \
                    "Promotional sales should not exceed total sales"
                print("✓ Promotional sales <= Total sales")
    
    # Test 9: Sales value ranges
    # Check Unit Sales range
    unit_sales = df['Unit Sales'].dropna()
    if len(unit_sales) > 0:
        assert unit_sales.min() >= 0, "Unit Sales should not be negative"
        assert unit_sales.max() <= 1000000, f"Unit Sales seems too high: {unit_sales.max()}"
        print(f"✓ Unit Sales range: {unit_sales.min():.2f} to {unit_sales.max():.2f}")
    
    # Check Value Sales range
    value_sales = df['Value Sales'].dropna()
    if len(value_sales) > 0:
        assert value_sales.min() >= 0, "Value Sales should not be negative"
        assert value_sales.max() <= 10000000, f"Value Sales seems too high: {value_sales.max()}"
        print(f"✓ Value Sales range: £{value_sales.min():.2f} to £{value_sales.max():.2f}")
    
    # Test 10: Distribution metrics
    dist_columns = [col for col in df.columns if 'Distribution' in col or 'Store' in col]
    if len(dist_columns) > 0:
        print(f"✓ Distribution columns found: {len(dist_columns)}")
    
    # Test 11: Price metrics
    price_columns = [col for col in df.columns if 'Price' in col or 'price' in col.lower()]
    if len(price_columns) > 0:
        print(f"✓ Price columns found: {len(price_columns)}")
        
        # Check that prices are positive
        for price_col in price_columns:
            if price_col in df.columns:
                prices = df[price_col].dropna()
                if len(prices) > 0:
                    assert prices.min() >= 0, f"{price_col} should not be negative"
    
    # Test 12: Heavy right skew in sales (realistic pattern)
    if len(value_sales) > 100:
        median_sales = value_sales.median()
        mean_sales = value_sales.mean()
        
        # Mean should be significantly higher than median (right skew)
        assert mean_sales > median_sales * 1.5, "Sales should show right skew (mean > median)"
        print(f"✓ Sales distribution shows right skew (mean/median ratio: {mean_sales/median_sales:.2f})")
    
    # Test 13: Rate of sale metrics
    ros_columns = [col for col in df.columns if 'Rate' in col or 'ROS' in col]
    if len(ros_columns) > 0:
        print(f"✓ Rate of sale columns found: {len(ros_columns)}")
    
    # Test 14: No completely empty rows
    empty_rows = df.isna().all(axis=1).sum()
    assert empty_rows == 0, f"Found {empty_rows} completely empty rows"
    print("✓ No completely empty rows")
    
    # Test 15: Reasonable number of records
    min_expected = 100000  # At minimum
    max_expected = 10000000  # At maximum
    assert min_expected <= len(df) <= max_expected, \
        f"Expected between {min_expected:,} and {max_expected:,} records, got {len(df):,}"
    print(f"✓ Record count reasonable: {len(df):,}")
    
    print("\n✅ All Fact Sales tests passed!")
    return True

if __name__ == "__main__":
    test_fact_sales()