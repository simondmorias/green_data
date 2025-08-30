import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_products_dimension():
    """Test that products dimension meets all requirements"""
    
    print("Testing Products Dimension...")
    
    # Load the generated data
    df = pd.read_csv('generated_data/products_dimension.csv')
    
    # Test 1: Record count
    assert len(df) == 100000, f"Expected 100,000 products, got {len(df)}"
    print("✓ Record count: 100,000")
    
    # Test 2: Required columns exist
    required_columns = [
        'Product Key', 'Product Description', 'Barcode Value',
        'Category Value', 'Needstate Value', 'Segment Value', 
        'Subsegment Value', 'Manufacturer Value', 'Brand Value',
        'Subbrand Value', 'Flavor Value', 'Total Size Value',
        'Size Group Value', 'Pack Format Value', 'Special Pack Type Value'
    ]
    
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"
    print(f"✓ All {len(required_columns)} required columns present")
    
    # Test 3: Product Key uniqueness and range
    assert df['Product Key'].nunique() == len(df), "Product Keys are not unique"
    assert df['Product Key'].min() >= 56627300, "Product Key below minimum range"
    assert df['Product Key'].max() <= 2063367030, "Product Key above maximum range"
    print("✓ Product Keys are unique and in valid range")
    
    # Test 4: Barcode uniqueness
    assert df['Barcode Value'].nunique() == len(df), "Barcodes are not unique"
    print("✓ Barcodes are unique")
    
    # Test 5: Manufacturer count
    num_manufacturers = df['Manufacturer Value'].nunique()
    assert num_manufacturers == 50, f"Expected 50 manufacturers, got {num_manufacturers}"
    print("✓ Manufacturer count: 50")
    
    # Test 6: Brand count
    num_brands = df['Brand Value'].nunique()
    assert 390 <= num_brands <= 410, f"Expected ~400 brands, got {num_brands}"
    print(f"✓ Brand count: {num_brands}")
    
    # Test 7: Big Bite Chocolates validation
    big_bite_products = df[df['Manufacturer Value'] == 'BIG BITE CHOCOLATES']
    assert len(big_bite_products) == 200, f"Big Bite should have 200 products, got {len(big_bite_products)}"
    
    big_bite_brands = big_bite_products['Brand Value'].nunique()
    assert big_bite_brands == 4, f"Big Bite should have 4 brands, got {big_bite_brands}"
    
    # Count product ranges (unique brand-subsegment combinations)
    big_bite_ranges = big_bite_products.groupby(['Brand Value', 'Subsegment Value']).size().count()
    assert 13 <= big_bite_ranges <= 17, f"Big Bite should have ~15 product ranges, got {big_bite_ranges}"
    print("✓ Big Bite Chocolates: 200 products, 4 brands, appropriate product ranges")
    
    # Test 8: Category Value
    assert df['Category Value'].nunique() == 1, "Should only have CONFECTIONERY category"
    assert df['Category Value'].iloc[0] == 'CONFECTIONERY', "Category should be CONFECTIONERY"
    print("✓ Category Value: CONFECTIONERY")
    
    # Test 9: Needstate distribution
    needstate_dist = df['Needstate Value'].value_counts(normalize=True)
    
    if 'CHOCOLATE CONFECTIONERY' in needstate_dist.index:
        choc_pct = needstate_dist['CHOCOLATE CONFECTIONERY']
        assert 0.70 <= choc_pct <= 0.80, f"Chocolate should be ~75% of products, got {choc_pct:.1%}"
    
    if 'SUGAR CONFECTIONERY' in needstate_dist.index:
        sugar_pct = needstate_dist['SUGAR CONFECTIONERY']
        assert 0.15 <= sugar_pct <= 0.25, f"Sugar should be ~20% of products, got {sugar_pct:.1%}"
    
    print("✓ Needstate distribution within expected ranges")
    
    # Test 10: Segment distribution (for Chocolate Confectionery)
    choc_products = df[df['Needstate Value'] == 'CHOCOLATE CONFECTIONERY']
    if len(choc_products) > 0:
        segment_dist = choc_products['Segment Value'].value_counts(normalize=True)
        
        # Check major segments exist and have reasonable distribution
        expected_segments = ['BARS / COUNTLINES', 'BLOCKS & TABLETS', 'SHARING BAGS & POUCHES']
        for seg in expected_segments:
            if seg in segment_dist.index:
                assert segment_dist[seg] > 0.05, f"{seg} should be at least 5% of chocolate products"
        
        print("✓ Segment distribution validated")
    
    # Test 11: Flavor Value (should replace Fragrance)
    assert 'Flavor Value' in df.columns, "Flavor Value column missing"
    assert 'Fragrance Value' not in df.columns, "Fragrance Value should be replaced with Flavor Value"
    
    # Check flavor distribution
    flavor_dist = df['Flavor Value'].value_counts(normalize=True)
    expected_flavors = ['MILK CHOCOLATE', 'DARK CHOCOLATE', 'WHITE CHOCOLATE']
    
    for flavor in expected_flavors:
        if flavor in flavor_dist.index:
            assert flavor_dist[flavor] > 0.02, f"{flavor} should be at least 2% of products"
    
    print("✓ Flavor Value column present with expected values")
    
    # Test 12: Pack Format distribution
    pack_format_dist = df['Pack Format Value'].value_counts(normalize=True)
    
    if 'SINGLE PACK' in pack_format_dist.index:
        single_pct = pack_format_dist['SINGLE PACK']
        assert 0.80 <= single_pct <= 0.90, f"Single packs should be ~85%, got {single_pct:.1%}"
    
    if 'MULTIPACK' in pack_format_dist.index:
        multi_pct = pack_format_dist['MULTIPACK']
        assert 0.10 <= multi_pct <= 0.20, f"Multipacks should be ~15%, got {multi_pct:.1%}"
    
    print("✓ Pack format distribution validated")
    
    # Test 13: Size patterns
    # Check that multipacks have format like "4 X 45G" in Total Size Value
    multipacks = df[df['Pack Format Value'] == 'MULTIPACK']['Total Size Value']
    if len(multipacks) > 0:
        # Sample check - at least some should have X pattern
        x_pattern_count = multipacks.str.contains('X', case=False, na=False).sum()
        assert x_pattern_count > len(multipacks) * 0.5, "Multipacks should have 'X' format in size"
    
    print("✓ Size patterns validated")
    
    # Test 14: Private Label presence
    private_label_count = len(df[df['Manufacturer Value'].str.contains('PRIVATE LABEL', case=False, na=False)])
    private_label_pct = private_label_count / len(df)
    assert 0.10 <= private_label_pct <= 0.25, f"Private label should be 15-20% of products, got {private_label_pct:.1%}"
    print(f"✓ Private label presence: {private_label_pct:.1%}")
    
    # Test 15: Seasonal products
    # Check for seasonal keywords in descriptions or segments
    seasonal_keywords = ['CHRISTMAS', 'EASTER', 'VALENTINE', 'SEASONAL', 'ADVENT', 'EGG']
    seasonal_mask = df['Product Description'].str.contains('|'.join(seasonal_keywords), case=False, na=False)
    seasonal_pct = seasonal_mask.sum() / len(df)
    assert 0.03 <= seasonal_pct <= 0.10, f"Seasonal products should be ~5% of total, got {seasonal_pct:.1%}"
    print(f"✓ Seasonal products: {seasonal_pct:.1%}")
    
    # Test 16: Product Description format
    # Should contain brand, subsegment, flavor, size, barcode
    sample_descriptions = df['Product Description'].head(10)
    for desc in sample_descriptions:
        # Check if description has multiple components
        assert len(desc.split()) >= 3, f"Product description too short: {desc}"
    print("✓ Product descriptions properly formatted")
    
    # Test 17: Top manufacturers market share
    manufacturer_counts = df['Manufacturer Value'].value_counts()
    top_5_share = manufacturer_counts.head(5).sum() / len(df)
    assert 0.30 <= top_5_share <= 0.50, f"Top 5 manufacturers should have ~40% share, got {top_5_share:.1%}"
    print(f"✓ Top 5 manufacturers market share: {top_5_share:.1%}")
    
    print("\n✅ All Products Dimension tests passed!")
    return True

if __name__ == "__main__":
    test_products_dimension()