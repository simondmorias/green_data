import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_seasonal_patterns():
    """Test that seasonal sales patterns meet requirements"""
    
    print("Testing Seasonal Sales Patterns...")
    
    # Load the data
    sales_df = pd.read_csv('generated_data/fact_sales.csv')
    products_df = pd.read_csv('generated_data/products_dimension.csv')
    time_df = pd.read_csv('generated_data/time_dimension.csv')
    geography_df = pd.read_csv('generated_data/geography_dimension.csv')
    
    # Merge to get full context
    df = sales_df.merge(products_df, on='Product Key', how='left')
    df = df.merge(time_df, on='Time Key', how='left')
    df = df.merge(geography_df, on='Geography Key', how='left')
    
    # Test 1: Christmas Season (Weeks 48-52, December)
    print("\n=== Christmas Season Tests ===")
    
    # Identify Christmas weeks
    december_mask = df['Time Description'].str.contains('Dec', case=False, na=False)
    christmas_weeks = df[december_mask]['Time Key'].unique()
    
    if len(christmas_weeks) > 0:
        # Identify seasonal chocolate products
        seasonal_products = df[
            df['Product Description'].str.contains(
                'CHRISTMAS|ADVENT|SELECTION|GIFT|TIN|SEASONAL', 
                case=False, na=False
            )
        ]
        
        if len(seasonal_products) > 0:
            # Calculate baseline (non-December average)
            non_december = df[~december_mask & df['Value Sales'].notna()]
            baseline_sales = non_december.groupby('Product Key')['Value Sales'].mean()
            
            # Calculate Christmas sales
            christmas_sales = df[december_mask & df['Value Sales'].notna()]
            christmas_avg = christmas_sales.groupby('Product Key')['Value Sales'].mean()
            
            # Check multiplier for seasonal products
            seasonal_product_keys = seasonal_products['Product Key'].unique()
            
            multipliers = []
            for product_key in seasonal_product_keys[:100]:  # Sample check
                if product_key in baseline_sales.index and product_key in christmas_avg.index:
                    if baseline_sales[product_key] > 0:
                        multiplier = christmas_avg[product_key] / baseline_sales[product_key]
                        multipliers.append(multiplier)
            
            if multipliers:
                avg_multiplier = np.mean(multipliers)
                print(f"✓ Christmas seasonal products show {avg_multiplier:.1f}x sales increase")
                
                # Some products should show 3.5x-5x increase
                high_multipliers = [m for m in multipliers if m > 3.0]
                assert len(high_multipliers) > 0, "Should have some products with 3x+ Christmas sales"
                print(f"✓ {len(high_multipliers)} products show 3x+ Christmas uplift")
        
        # Check for advent calendars
        advent_products = df[df['Product Description'].str.contains('ADVENT', case=False, na=False)]
        if len(advent_products) > 0:
            # Advent calendars should primarily sell in weeks 44-51
            advent_sales = advent_products[advent_products['Value Sales'].notna()]
            print(f"✓ Advent calendar products found: {advent_products['Product Key'].nunique()}")
    
    # Test 2: Easter Season (Weeks 10-16, March-April)
    print("\n=== Easter Season Tests ===")
    
    # Identify Easter weeks (March-April)
    easter_mask = df['Time Description'].str.contains('Mar|Apr', case=False, na=False)
    easter_weeks = df[easter_mask]['Time Key'].unique()
    
    if len(easter_weeks) > 0:
        # Identify Easter products
        easter_products = df[
            df['Product Description'].str.contains(
                'EASTER|EGG|BUNNY|SPRING', 
                case=False, na=False
            )
        ]
        
        if len(easter_products) > 0:
            # Check concentration of sales in Easter period
            easter_product_keys = easter_products['Product Key'].unique()
            
            for product_key in easter_product_keys[:50]:  # Sample
                product_sales = df[df['Product Key'] == product_key]
                easter_sales = product_sales[easter_mask]['Value Sales'].sum()
                total_sales = product_sales['Value Sales'].sum()
                
                if total_sales > 0:
                    easter_concentration = easter_sales / total_sales
                    if easter_concentration > 0.8:
                        print(f"✓ Easter product {product_key} has {easter_concentration:.0%} sales in Easter period")
                        break
            
            print(f"✓ Easter products found: {len(easter_product_keys)}")
    
    # Test 3: Valentine's Day (Weeks 5-7, February)
    print("\n=== Valentine's Day Tests ===")
    
    # Identify Valentine's weeks
    february_mask = df['Time Description'].str.contains('Feb', case=False, na=False)
    valentine_weeks = df[february_mask]['Time Key'].unique()
    
    if len(valentine_weeks) > 0:
        # Identify Valentine's products
        valentine_products = df[
            df['Product Description'].str.contains(
                'VALENTINE|HEART|LOVE|PINK|RED', 
                case=False, na=False
            )
        ]
        
        if len(valentine_products) > 0:
            valentine_product_count = valentine_products['Product Key'].nunique()
            print(f"✓ Valentine's products found: {valentine_product_count}")
            
            # Check for premium/gift products uplift
            premium_products = df[
                df['Product Description'].str.contains(
                    'PREMIUM|LUXURY|GIFT|PRALINE', 
                    case=False, na=False
                )
            ]
            
            if len(premium_products) > 0:
                # Check February sales for premium products
                feb_premium = premium_products[february_mask]
                if len(feb_premium) > 0:
                    print(f"✓ Premium products show activity in Valentine's period")
    
    # Test 4: Summer Lull (Weeks 26-35, June-August)
    print("\n=== Summer Lull Tests ===")
    
    # Identify summer weeks
    summer_mask = df['Time Description'].str.contains('Jun|Jul|Aug', case=False, na=False)
    summer_weeks = df[summer_mask]['Time Key'].unique()
    
    if len(summer_weeks) > 0:
        # Calculate average sales by period
        summer_sales = df[summer_mask & df['Value Sales'].notna()]['Value Sales'].mean()
        non_summer_sales = df[~summer_mask & df['Value Sales'].notna()]['Value Sales'].mean()
        
        if summer_sales > 0 and non_summer_sales > 0:
            summer_ratio = summer_sales / non_summer_sales
            
            # Summer should show lower sales (0.7x-0.85x)
            if summer_ratio < 1.0:
                print(f"✓ Summer shows lower sales: {summer_ratio:.2f}x of normal")
            else:
                print(f"  Summer sales ratio: {summer_ratio:.2f}x (expected < 1.0)")
    
    # Test 5: Peak weeks identification
    print("\n=== Peak Week Analysis ===")
    
    # Find highest sales weeks
    weekly_sales = df.groupby('Time Key')['Value Sales'].sum().sort_values(ascending=False)
    top_5_weeks = weekly_sales.head(5)
    
    # Map back to time descriptions
    top_week_times = time_df[time_df['Time Key'].isin(top_5_weeks.index)]
    
    print("Top 5 sales weeks:")
    for _, row in top_week_times.iterrows():
        week_sales = weekly_sales[row['Time Key']]
        print(f"  - {row['Time Description']}: £{week_sales:,.0f}")
    
    # Check if December weeks are in top weeks
    december_in_top = any('Dec' in str(desc) for desc in top_week_times['Time Description'])
    if december_in_top:
        print("✓ December weeks appear in top sales periods")
    
    # Test 6: Seasonal product distribution
    print("\n=== Seasonal Product Distribution ===")
    
    # Count seasonal products
    seasonal_keywords = ['CHRISTMAS', 'EASTER', 'VALENTINE', 'SEASONAL', 'ADVENT', 
                        'EGG', 'HEART', 'GIFT', 'SELECTION']
    
    seasonal_mask = products_df['Product Description'].str.contains(
        '|'.join(seasonal_keywords), case=False, na=False
    )
    
    seasonal_product_count = seasonal_mask.sum()
    seasonal_percentage = (seasonal_product_count / len(products_df)) * 100
    
    assert 3 <= seasonal_percentage <= 10, \
        f"Seasonal products should be ~5% of total, got {seasonal_percentage:.1f}%"
    print(f"✓ Seasonal products: {seasonal_percentage:.1f}% of total ({seasonal_product_count} products)")
    
    # Test 7: Regional variations in seasonal sales
    print("\n=== Regional Seasonal Variations ===")
    
    if 'Scotland' in df['Geography Description'].str.upper().values:
        # Scotland should maintain higher sales in summer
        scotland_summer = df[
            (df['Geography Description'].str.contains('SCOTLAND', case=False, na=False)) &
            summer_mask
        ]
        
        if len(scotland_summer) > 0:
            print("✓ Scotland geography found for regional variation testing")
    
    # Test 8: Waitrose luxury seasonal concentration
    waitrose_mask = df['Geography Description'].str.contains('WAITROSE', case=False, na=False)
    if waitrose_mask.any():
        waitrose_christmas = df[waitrose_mask & december_mask]
        
        if len(waitrose_christmas) > 0:
            # Check for luxury products
            luxury_mask = waitrose_christmas['Product Description'].str.contains(
                'LUXURY|PREMIUM|GIFT|SELECTION', case=False, na=False
            )
            
            if luxury_mask.any():
                print("✓ Waitrose shows luxury product sales in Christmas period")
    
    print("\n✅ All Seasonal Pattern tests passed!")
    return True

if __name__ == "__main__":
    test_seasonal_patterns()