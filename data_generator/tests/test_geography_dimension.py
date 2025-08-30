import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_geography_dimension():
    """Test that geography dimension meets all requirements"""
    
    print("Testing Geography Dimension...")
    
    # Load the generated data
    df = pd.read_csv('generated_data/geography_dimension.csv')
    
    # Test 1: Required columns
    required_columns = ['Geography Key', 'Geography Description']
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"
    print("✓ All required columns present")
    
    # Test 2: Geography Key uniqueness and range
    assert df['Geography Key'].nunique() == len(df), "Geography Keys are not unique"
    assert df['Geography Key'].min() >= 27000000, f"Geography Key below minimum range: {df['Geography Key'].min()}"
    assert df['Geography Key'].max() <= 27999999, f"Geography Key above maximum range: {df['Geography Key'].max()}"
    print("✓ Geography Keys are unique and in valid range (27000000-27999999)")
    
    # Test 3: Expected retailers present
    expected_retailers = [
        'IRI All Outlets',
        'Tesco', 'Sainsburys', 'Asda', 'Morrisons', 'Waitrose', 'Co-op',
        'Aldi', 'Lidl',
        'Boots', 'Superdrug'
    ]
    
    descriptions = df['Geography Description'].str.upper().unique()
    
    for retailer in expected_retailers:
        retailer_upper = retailer.upper()
        found = any(retailer_upper in desc for desc in descriptions)
        assert found, f"Expected retailer not found: {retailer}"
    
    print("✓ All major retailers present")
    
    # Test 4: Online channels present
    online_retailers = ['ONLINE', 'DIGITAL', '.COM']
    online_count = 0
    for desc in descriptions:
        if any(online in desc for online in online_retailers):
            online_count += 1
    
    assert online_count >= 4, f"Expected at least 4 online channels, found {online_count}"
    print(f"✓ Online channels present: {online_count} found")
    
    # Test 5: Convenience channels
    convenience_keywords = ['CONVENIENCE', 'SPAR', 'LONDIS', 'COSTCUTTER', 'LOCAL']
    convenience_count = 0
    for desc in descriptions:
        if any(conv in desc for conv in convenience_keywords):
            convenience_count += 1
    
    assert convenience_count >= 2, f"Expected at least 2 convenience channels, found {convenience_count}"
    print(f"✓ Convenience channels present: {convenience_count} found")
    
    # Test 6: IRI All Outlets aggregate
    iri_present = any('IRI ALL OUTLETS' in desc or 'ALL OUTLETS' in desc for desc in descriptions)
    assert iri_present, "IRI All Outlets (aggregate) should be present"
    print("✓ IRI All Outlets aggregate present")
    
    # Test 7: Reasonable number of geographies
    total_geographies = len(df)
    assert 20 <= total_geographies <= 100, f"Expected 20-100 geography entries, got {total_geographies}"
    print(f"✓ Total geographies: {total_geographies}")
    
    # Test 8: Discounters present
    discounters = ['ALDI', 'LIDL', 'POUNDLAND', 'HOME BARGAINS']
    discounter_count = 0
    for desc in descriptions:
        if any(disc in desc for disc in discounters):
            discounter_count += 1
    
    assert discounter_count >= 2, f"Expected at least 2 discounters, found {discounter_count}"
    print(f"✓ Discounters present: {discounter_count} found")
    
    # Test 9: Health & Beauty channels
    health_beauty = ['BOOTS', 'SUPERDRUG']
    hb_count = 0
    for desc in descriptions:
        if any(hb in desc for hb in health_beauty):
            hb_count += 1
    
    assert hb_count >= 2, f"Expected at least 2 health & beauty channels, found {hb_count}"
    print(f"✓ Health & Beauty channels: {hb_count} found")
    
    # Test 10: No duplicate descriptions
    assert df['Geography Description'].nunique() == len(df), "Geography descriptions should be unique"
    print("✓ All geography descriptions are unique")
    
    # Test 11: Format-specific stores (e.g., Tesco Express, Sainsbury's Local)
    format_keywords = ['EXPRESS', 'LOCAL', 'METRO', 'EXTRA', 'SUPERSTORE']
    format_count = 0
    for desc in descriptions:
        if any(fmt in desc for fmt in format_keywords):
            format_count += 1
    
    print(f"✓ Store formats found: {format_count} (Express, Local, Metro, etc.)")
    
    # Test 12: Regional variations might exist
    regional_keywords = ['SCOTLAND', 'WALES', 'NORTHERN IRELAND', 'LONDON', 'NORTH', 'SOUTH']
    regional_count = 0
    for desc in descriptions:
        if any(region in desc for region in regional_keywords):
            regional_count += 1
    
    if regional_count > 0:
        print(f"✓ Regional variations found: {regional_count}")
    
    # Test 13: Wholesale channels
    wholesale_keywords = ['COSTCO', 'BOOKER', 'WHOLESALE', 'CASH & CARRY']
    wholesale_count = 0
    for desc in descriptions:
        if any(wholesale in desc for wholesale in wholesale_keywords):
            wholesale_count += 1
    
    if wholesale_count > 0:
        print(f"✓ Wholesale channels found: {wholesale_count}")
    
    print("\n✅ All Geography Dimension tests passed!")
    return True

if __name__ == "__main__":
    test_geography_dimension()