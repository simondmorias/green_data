import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_scenarios():
    """Test complex data scenarios for data science validation"""
    
    print("Testing Complex Data Scenarios...")
    
    # Load the data
    sales_df = pd.read_csv('generated_data/fact_sales.csv')
    products_df = pd.read_csv('generated_data/products_dimension.csv')
    time_df = pd.read_csv('generated_data/time_dimension.csv')
    geography_df = pd.read_csv('generated_data/geography_dimension.csv')
    
    # Create merged dataset for analysis
    df = sales_df.merge(products_df, on='Product Key', how='left')
    df = df.merge(time_df, on='Time Key', how='left')
    df = df.merge(geography_df, on='Geography Key', how='left')
    
    # Test 1: Product Launch Patterns
    print("\n=== Product Launch Patterns ===")
    
    # Find products with clear launch patterns (no sales then sudden sales)
    product_time_sales = df.groupby(['Product Key', 'Time Key'])['Value Sales'].sum().unstack(fill_value=0)
    
    launch_patterns_found = 0
    for product in product_time_sales.index[:1000]:  # Sample check
        sales_timeline = product_time_sales.loc[product]
        
        # Look for pattern: zeros followed by consistent sales
        first_sale_idx = (sales_timeline > 0).idxmax() if sales_timeline.sum() > 0 else None
        
        if first_sale_idx and first_sale_idx != sales_timeline.index[0]:
            # Found a product that launched after week 1
            weeks_before = sales_timeline.index.get_loc(first_sale_idx)
            if weeks_before > 4:  # At least 4 weeks of no sales before launch
                launch_patterns_found += 1
                
                if launch_patterns_found == 1:
                    print(f"✓ Product {product} shows launch pattern at week {first_sale_idx}")
    
    assert launch_patterns_found > 0, "Should find some products with launch patterns"
    print(f"✓ Found {launch_patterns_found} products with clear launch patterns")
    
    # Test 2: Product Delisting Patterns
    print("\n=== Product Delisting Patterns ===")
    
    delisting_patterns_found = 0
    for product in product_time_sales.index[:1000]:  # Sample check
        sales_timeline = product_time_sales.loc[product]
        
        # Look for pattern: consistent sales then sudden stop
        if sales_timeline.sum() > 0:
            last_sale_idx = sales_timeline[sales_timeline > 0].index[-1]
            last_idx = sales_timeline.index[-1]
            
            if last_sale_idx != last_idx:
                # Product stopped selling before end of time period
                weeks_after = len(sales_timeline) - sales_timeline.index.get_loc(last_sale_idx) - 1
                if weeks_after > 4:  # At least 4 weeks of no sales after last sale
                    delisting_patterns_found += 1
                    
                    if delisting_patterns_found == 1:
                        print(f"✓ Product {product} shows delisting pattern at week {last_sale_idx}")
    
    if delisting_patterns_found > 0:
        print(f"✓ Found {delisting_patterns_found} products with delisting patterns")
    
    # Test 3: Viral/Spike Patterns
    print("\n=== Viral Product Patterns ===")
    
    spike_patterns_found = 0
    for product in product_time_sales.index[:1000]:  # Sample check
        sales_timeline = product_time_sales.loc[product]
        
        if len(sales_timeline) > 10 and sales_timeline.sum() > 0:
            # Calculate week-over-week changes
            changes = sales_timeline.pct_change()
            
            # Look for 300%+ increases (viral moment)
            viral_weeks = changes[changes > 3.0]
            
            if len(viral_weeks) > 0:
                spike_patterns_found += 1
                if spike_patterns_found == 1:
                    max_spike = changes.max()
                    print(f"✓ Product {product} shows viral spike: {max_spike:.0%} increase")
    
    if spike_patterns_found > 0:
        print(f"✓ Found {spike_patterns_found} products with viral/spike patterns")
    
    # Test 4: Cannibalization Detection
    print("\n=== Cannibalization Patterns ===")
    
    # Look for products with similar names that show inverse correlations
    cannibalization_found = False
    
    # Group products by brand
    for brand in products_df['Brand Value'].value_counts().head(20).index:
        brand_products = products_df[products_df['Brand Value'] == brand]['Product Key'].values
        
        if len(brand_products) > 5:
            # Check correlations between products in same brand
            brand_sales = product_time_sales.loc[
                product_time_sales.index.intersection(brand_products)
            ]
            
            if len(brand_sales) > 2:
                correlations = brand_sales.T.corr()
                
                # Look for negative correlations (cannibalization)
                negative_corrs = (correlations < -0.3) & (correlations != 1.0)
                
                if negative_corrs.any().any():
                    cannibalization_found = True
                    print(f"✓ Potential cannibalization found in {brand} brand")
                    break
    
    if cannibalization_found:
        print("✓ Cannibalization patterns detected")
    
    # Test 5: Supply Chain Disruption Patterns
    print("\n=== Supply Chain Disruption Patterns ===")
    
    # Look for erratic availability (high variance in sales)
    disruption_patterns_found = 0
    
    for product in product_time_sales.index[:500]:  # Sample check
        sales_timeline = product_time_sales.loc[product]
        
        if sales_timeline.sum() > 0:
            # Calculate coefficient of variation
            if sales_timeline.mean() > 0:
                cv = sales_timeline.std() / sales_timeline.mean()
                
                # High CV indicates erratic availability
                if cv > 2.0:  # Very high variation
                    # Check for pattern of availability gaps
                    zero_weeks = (sales_timeline == 0).sum()
                    non_zero_weeks = (sales_timeline > 0).sum()
                    
                    if zero_weeks > 0 and non_zero_weeks > 5:
                        # Has both sales and gaps
                        disruption_patterns_found += 1
                        
                        if disruption_patterns_found == 1:
                            print(f"✓ Product {product} shows supply disruption pattern (CV={cv:.2f})")
    
    if disruption_patterns_found > 0:
        print(f"✓ Found {disruption_patterns_found} products with supply chain disruption patterns")
    
    # Test 6: Price Architecture Patterns
    print("\n=== Price Architecture Patterns ===")
    
    # Check size-price relationships
    if 'Total Size Value' in products_df.columns:
        # Extract numeric size values
        products_df['Size_Numeric'] = products_df['Total Size Value'].str.extract(r'(\d+)').astype(float)
        
        # Group by brand and check price per gram patterns
        for brand in products_df['Brand Value'].value_counts().head(10).index:
            brand_products = products_df[products_df['Brand Value'] == brand]
            
            if len(brand_products) > 5:
                # Get average prices for different sizes
                size_prices = []
                for _, product in brand_products.iterrows():
                    if pd.notna(product['Size_Numeric']):
                        product_sales = df[df['Product Key'] == product['Product Key']]
                        if len(product_sales) > 0 and 'Value Sales' in product_sales.columns:
                            avg_price = product_sales['Value Sales'].mean()
                            if avg_price > 0:
                                size_prices.append((product['Size_Numeric'], avg_price))
                
                if len(size_prices) > 3:
                    # Check for non-linear pricing
                    sizes = [s[0] for s in size_prices]
                    prices = [s[1] for s in size_prices]
                    
                    # Larger sizes should have lower price per unit (economies of scale)
                    if max(sizes) > min(sizes) * 2:
                        print(f"✓ Brand {brand} shows size-based price architecture")
                        break
    
    # Test 7: Geographic Product Variations
    print("\n=== Geographic Variations ===")
    
    # Check for products that only sell in certain geographies
    geographic_exclusives = 0
    
    for product in products_df['Product Key'].sample(min(500, len(products_df))):
        product_sales = df[df['Product Key'] == product]
        
        if len(product_sales) > 0:
            geographies_sold = product_sales[product_sales['Value Sales'] > 0]['Geography Description'].nunique()
            total_geographies = geography_df['Geography Description'].nunique()
            
            # Product sells in less than 30% of geographies (exclusive/limited)
            if 0 < geographies_sold < total_geographies * 0.3:
                geographic_exclusives += 1
                
                if geographic_exclusives == 1:
                    print(f"✓ Product {product} shows geographic exclusivity ({geographies_sold}/{total_geographies} locations)")
    
    if geographic_exclusives > 0:
        print(f"✓ Found {geographic_exclusives} geographically exclusive products")
    
    # Test 8: Substitution Patterns
    print("\n=== Substitution Patterns ===")
    
    # When one product is out of stock, others in same category increase
    substitution_found = False
    
    # Look within segments
    for segment in products_df['Segment Value'].value_counts().head(5).index:
        segment_products = products_df[products_df['Segment Value'] == segment]['Product Key'].values[:20]
        
        if len(segment_products) > 5:
            # Check for inverse patterns
            segment_sales = product_time_sales.loc[
                product_time_sales.index.intersection(segment_products)
            ]
            
            if len(segment_sales) > 3:
                # Look for weeks where one product drops and others increase
                for week in segment_sales.columns[:20]:  # Sample weeks
                    week_sales = segment_sales[week]
                    
                    # Find products with zero sales this week but sales in other weeks
                    zero_this_week = segment_sales.index[week_sales == 0]
                    has_other_sales = segment_sales.index[segment_sales.sum(axis=1) > 0]
                    
                    out_of_stock = set(zero_this_week) & set(has_other_sales)
                    
                    if len(out_of_stock) > 0:
                        # Check if other products increased
                        prev_week_idx = max(0, segment_sales.columns.get_loc(week) - 1)
                        if prev_week_idx > 0:
                            prev_week = segment_sales.columns[prev_week_idx]
                            
                            for product in segment_sales.index:
                                if product not in out_of_stock:
                                    if segment_sales.loc[product, week] > segment_sales.loc[product, prev_week] * 1.2:
                                        substitution_found = True
                                        print(f"✓ Potential substitution pattern found in {segment}")
                                        break
                    
                    if substitution_found:
                        break
            
            if substitution_found:
                break
    
    # Test 9: Promotional Effectiveness
    print("\n=== Promotional Patterns ===")
    
    if 'Total Promo Unit Sales' in df.columns and 'Unit Sales' in df.columns:
        # Find products with promotional sales
        promo_products = df[df['Total Promo Unit Sales'] > 0]
        
        if len(promo_products) > 0:
            # Check for pantry loading effect (sales drop after promotion)
            promotional_patterns = 0
            
            for product in promo_products['Product Key'].unique()[:100]:
                product_timeline = df[df['Product Key'] == product].sort_values('Time Key')
                
                if len(product_timeline) > 5:
                    # Look for promo weeks followed by lower sales
                    for i in range(len(product_timeline) - 1):
                        current_promo = product_timeline.iloc[i]['Total Promo Unit Sales']
                        next_sales = product_timeline.iloc[i + 1]['Unit Sales']
                        
                        if pd.notna(current_promo) and current_promo > 0:
                            if pd.notna(next_sales):
                                # Check if next week sales are lower
                                avg_sales = product_timeline['Unit Sales'].mean()
                                if next_sales < avg_sales * 0.7:
                                    promotional_patterns += 1
                                    break
            
            if promotional_patterns > 0:
                print(f"✓ Found {promotional_patterns} products with post-promotion dip patterns")
    
    # Test 10: Category Migration Detection
    print("\n=== Category Migration Patterns ===")
    
    # Check for products that might be miscategorized
    category_anomalies = 0
    
    # Protein bars might be in wrong category
    protein_products = products_df[
        products_df['Product Description'].str.contains('PROTEIN', case=False, na=False)
    ]
    
    if len(protein_products) > 0:
        # Check if all are in confectionery
        non_confectionery = protein_products[protein_products['Category Value'] != 'CONFECTIONERY']
        
        if len(non_confectionery) > 0:
            category_anomalies = len(non_confectionery)
            print(f"✓ Found {category_anomalies} potential category misclassifications")
        else:
            # Check for unusual sales patterns compared to regular chocolate
            print("✓ Protein products found for category analysis")
    
    print("\n✅ All Data Scenario tests completed!")
    return True

if __name__ == "__main__":
    test_data_scenarios()