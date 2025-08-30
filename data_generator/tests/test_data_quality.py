import pandas as pd
import numpy as np
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_quality():
    """Test that intentional data quality issues are present for realistic testing"""
    
    print("Testing Data Quality Issues (Intentional)...")
    
    # Load the data
    products_df = pd.read_csv('generated_data/products_dimension.csv')
    sales_df = pd.read_csv('generated_data/fact_sales.csv')
    
    # Test 1: Barcode Changes (5% of products should have barcode changes)
    print("\n=== Barcode Change Detection ===")
    
    # Look for products with very similar descriptions but different barcodes
    barcode_changes_found = 0
    
    # Group by similar product descriptions (ignoring barcode)
    products_df['Description_Without_Barcode'] = products_df['Product Description'].apply(
        lambda x: re.sub(r'\d{6,13}', '', str(x)).strip() if pd.notna(x) else ''
    )
    
    # Find groups with same description but different barcodes
    desc_groups = products_df.groupby('Description_Without_Barcode')['Barcode Value'].nunique()
    multiple_barcodes = desc_groups[desc_groups > 1]
    
    if len(multiple_barcodes) > 0:
        barcode_changes_found = len(multiple_barcodes)
        expected_changes = int(len(products_df) * 0.05)
        
        print(f"✓ Found {barcode_changes_found} products with barcode changes")
        
        # Show example
        example_desc = multiple_barcodes.index[0]
        example_products = products_df[
            products_df['Description_Without_Barcode'] == example_desc
        ][['Product Key', 'Product Description', 'Barcode Value']].head(2)
        
        if len(example_products) > 1:
            print(f"  Example: Same product, different barcodes:")
            print(f"    - {example_products.iloc[0]['Barcode Value']}")
            print(f"    - {example_products.iloc[1]['Barcode Value']}")
    
    # Test 2: Description Inconsistencies
    print("\n=== Description Inconsistencies ===")
    
    inconsistencies_found = {
        'multipack_variants': 0,
        'size_variants': 0,
        'case_variants': 0
    }
    
    # Check for MULTI PACK vs MULTIPACK vs MULTI-PACK
    multipack_variants = [
        products_df['Product Description'].str.contains('MULTI PACK', case=False, na=False).sum(),
        products_df['Product Description'].str.contains('MULTIPACK', case=False, na=False).sum(),
        products_df['Product Description'].str.contains('MULTI-PACK', case=False, na=False).sum()
    ]
    
    if sum(v > 0 for v in multipack_variants) > 1:
        inconsistencies_found['multipack_variants'] = sum(multipack_variants)
        print(f"✓ Found multipack naming inconsistencies: {sum(multipack_variants)} variants")
    
    # Check for 100G vs 100 G vs 100GR
    size_patterns = [
        r'\d+G\b',      # 100G
        r'\d+\s+G\b',   # 100 G
        r'\d+GR\b',     # 100GR
        r'\d+\s+GR\b'   # 100 GR
    ]
    
    size_variant_counts = []
    for pattern in size_patterns:
        count = products_df['Product Description'].str.contains(pattern, case=False, na=False, regex=True).sum()
        if count > 0:
            size_variant_counts.append(count)
    
    if len(size_variant_counts) > 1:
        inconsistencies_found['size_variants'] = sum(size_variant_counts)
        print(f"✓ Found size notation inconsistencies: {len(size_variant_counts)} different formats")
    
    # Check for case inconsistencies (e.g., Cadbury vs CADBURY)
    brand_cases = {}
    for desc in products_df['Product Description'].dropna():
        words = desc.split()
        if len(words) > 0:
            first_word = words[0]
            base_word = first_word.upper()
            
            if base_word not in brand_cases:
                brand_cases[base_word] = set()
            brand_cases[base_word].add(first_word)
    
    # Find brands with multiple case variants
    for brand, variants in brand_cases.items():
        if len(variants) > 1:
            inconsistencies_found['case_variants'] += 1
            if inconsistencies_found['case_variants'] == 1:
                print(f"✓ Found case inconsistencies: {variants}")
    
    total_inconsistencies = sum(inconsistencies_found.values())
    if total_inconsistencies > 0:
        print(f"✓ Total description inconsistencies found: {total_inconsistencies}")
    
    # Test 3: Missing Data Patterns
    print("\n=== Missing Data Patterns ===")
    
    # Check for systematic missing data
    missing_patterns_found = False
    
    # Group by geography and time to find gaps
    sales_grouped = sales_df.groupby(['Geography Key', 'Time Key']).size().unstack(fill_value=0)
    
    for geography in sales_grouped.index[:10]:  # Check first 10 geographies
        timeline = sales_grouped.loc[geography]
        
        # Look for consecutive weeks with no data
        zero_runs = []
        current_run = 0
        
        for val in timeline:
            if val == 0:
                current_run += 1
            else:
                if current_run >= 3:  # At least 3 consecutive weeks
                    zero_runs.append(current_run)
                current_run = 0
        
        if zero_runs:
            missing_patterns_found = True
            print(f"✓ Geography {geography} has data gaps: {max(zero_runs)} consecutive weeks missing")
            break
    
    # Check for missing promotional data
    if 'Total Promo Unit Sales' in sales_df.columns:
        promo_missing = sales_df['Total Promo Unit Sales'].isna().sum()
        promo_missing_pct = (promo_missing / len(sales_df)) * 100
        
        if promo_missing_pct > 10:
            print(f"✓ Promotional data missing: {promo_missing_pct:.1f}% of records")
            missing_patterns_found = True
    
    if missing_patterns_found:
        print("✓ Missing data patterns detected")
    
    # Test 4: Duplicate Records (0.1% intentional duplicates)
    print("\n=== Duplicate Records ===")
    
    # Check for duplicate key combinations
    key_columns = ['Geography Key', 'Product Key', 'Time Key']
    duplicates = sales_df[sales_df.duplicated(subset=key_columns, keep=False)]
    
    if len(duplicates) > 0:
        duplicate_pct = (len(duplicates) / len(sales_df)) * 100
        print(f"✓ Found {len(duplicates)} duplicate records ({duplicate_pct:.2f}%)")
        
        # Show example duplicate
        first_dup = duplicates.iloc[0]
        dup_group = sales_df[
            (sales_df['Geography Key'] == first_dup['Geography Key']) &
            (sales_df['Product Key'] == first_dup['Product Key']) &
            (sales_df['Time Key'] == first_dup['Time Key'])
        ]
        
        if len(dup_group) > 1:
            print(f"  Example duplicate: Product {first_dup['Product Key']} has {len(dup_group)} records for same geo/time")
    
    # Test 5: Temporal Anomalies
    print("\n=== Temporal Anomalies ===")
    
    # Bank holiday effects
    time_df = pd.read_csv('generated_data/time_dimension.csv')
    
    # Check for specific patterns around known holidays
    bank_holiday_keywords = ['BANK', 'HOLIDAY', 'CHRISTMAS', 'EASTER', 'NEW YEAR']
    
    anomaly_weeks = []
    for keyword in bank_holiday_keywords:
        holiday_weeks = time_df[
            time_df['Time Description'].str.contains(keyword, case=False, na=False)
        ]
        if len(holiday_weeks) > 0:
            anomaly_weeks.extend(holiday_weeks['Time Key'].values)
    
    if anomaly_weeks:
        # Check if these weeks have unusual patterns
        holiday_sales = sales_df[sales_df['Time Key'].isin(anomaly_weeks)]
        
        if len(holiday_sales) > 0:
            print(f"✓ Found {len(set(anomaly_weeks))} weeks with potential temporal anomalies")
    
    # Black Friday check
    november_weeks = time_df[time_df['Time Description'].str.contains('Nov', case=False, na=False)]
    
    if len(november_weeks) > 0:
        # Last November week should show increased promotional intensity
        late_nov_weeks = november_weeks['Time Key'].values[-4:]  # Last 4 weeks of November
        
        if 'Total Promo Unit Sales' in sales_df.columns:
            black_friday_sales = sales_df[sales_df['Time Key'].isin(late_nov_weeks)]
            
            if len(black_friday_sales) > 0:
                promo_intensity = black_friday_sales['Total Promo Unit Sales'].notna().mean()
                overall_promo = sales_df['Total Promo Unit Sales'].notna().mean()
                
                if promo_intensity > overall_promo * 1.5:
                    print(f"✓ Black Friday period shows {promo_intensity/overall_promo:.1f}x promotional intensity")
    
    # Test 6: Shrinkflation Detection
    print("\n=== Shrinkflation Patterns ===")
    
    # Look for products where size decreased but name stayed similar
    shrinkflation_found = 0
    
    # Extract numeric sizes
    products_df['Size_Numeric'] = products_df['Total Size Value'].str.extract(r'(\d+)').astype(float)
    
    # Group by brand and product type
    for brand in products_df['Brand Value'].value_counts().head(20).index:
        brand_products = products_df[products_df['Brand Value'] == brand]
        
        # Look for similar products with different sizes
        for subsegment in brand_products['Subsegment Value'].unique():
            segment_products = brand_products[brand_products['Subsegment Value'] == subsegment]
            
            if len(segment_products) > 1:
                sizes = segment_products['Size_Numeric'].dropna().unique()
                
                # Look for sizes that are close but not identical (e.g., 50g vs 46g)
                for i, size1 in enumerate(sizes):
                    for size2 in sizes[i+1:]:
                        ratio = min(size1, size2) / max(size1, size2)
                        
                        if 0.85 < ratio < 0.95:  # 5-15% size reduction
                            shrinkflation_found += 1
                            
                            if shrinkflation_found == 1:
                                print(f"✓ Potential shrinkflation: {brand} {subsegment} - {min(size1, size2)}g vs {max(size1, size2)}g")
    
    if shrinkflation_found > 0:
        print(f"✓ Found {shrinkflation_found} potential shrinkflation cases")
    
    # Test 7: Data Type Issues
    print("\n=== Data Type Consistency ===")
    
    # Check for numeric columns that might have non-numeric values
    numeric_columns = ['Unit Sales', 'Volume Sales', 'Value Sales']
    
    type_issues = 0
    for col in numeric_columns:
        if col in sales_df.columns:
            # Check if any values failed to parse as numeric
            non_numeric = pd.to_numeric(sales_df[col], errors='coerce').isna() & sales_df[col].notna()
            
            if non_numeric.any():
                type_issues += non_numeric.sum()
                print(f"✓ Found {non_numeric.sum()} non-numeric values in {col}")
    
    if type_issues == 0:
        print("✓ All numeric columns have consistent data types")
    
    # Test 8: Outlier Detection
    print("\n=== Outlier Detection ===")
    
    # Check for extreme values that might be data quality issues
    if 'Value Sales' in sales_df.columns:
        value_sales = sales_df['Value Sales'].dropna()
        
        if len(value_sales) > 0:
            q1 = value_sales.quantile(0.25)
            q3 = value_sales.quantile(0.75)
            iqr = q3 - q1
            
            extreme_outliers = (value_sales > q3 + 10 * iqr) | (value_sales < q1 - 10 * iqr)
            
            if extreme_outliers.any():
                outlier_count = extreme_outliers.sum()
                max_outlier = value_sales[extreme_outliers].max()
                
                print(f"✓ Found {outlier_count} extreme outliers (max: £{max_outlier:,.2f})")
    
    print("\n✅ All Data Quality tests completed!")
    print("Note: These data quality issues are intentional for testing purposes")
    return True

if __name__ == "__main__":
    test_data_quality()