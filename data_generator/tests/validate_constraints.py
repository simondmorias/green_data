#!/usr/bin/env python3
"""
Validation script to verify all business rules and constraints are met in generated data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import sys


class DataValidator:
    """Validates generated data against all business rules"""
    
    def __init__(self):
        self.validation_results = []
        self.errors = []
        self.warnings = []
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all generated data files"""
        try:
            products = pd.read_csv('generated_data/products_dimension.csv')
            geography = pd.read_csv('generated_data/geography_dimension.csv')
            time = pd.read_csv('generated_data/time_dimension.csv')
            fact_sales = pd.read_csv('generated_data/fact_sales.csv')
            return products, geography, time, fact_sales
        except Exception as e:
            print(f"Error loading data: {e}")
            sys.exit(1)
    
    def validate_hierarchical_consistency(self, geography: pd.DataFrame, fact_sales: pd.DataFrame) -> bool:
        """Validate that parent geography sales > sum of children"""
        print("\n1. Validating Hierarchical Consistency...")
        
        # Get IRI All Outlets key
        iri_row = geography[geography['geography_description'] == 'IRI All Outlets']
        if iri_row.empty:
            self.errors.append("IRI All Outlets not found in geography")
            return False
        
        iri_key = iri_row['geography_key'].iloc[0]
        
        # Get level 1 stores (excluding IRI itself)
        level1 = geography[(geography['hierarchy_level'] == 1) & 
                          (geography['geography_key'] != iri_key)]
        
        # Check for sample of time periods
        time_keys = fact_sales['Time Key'].unique()[:10]  # Check first 10 periods
        
        hierarchy_valid = True
        for time_key in time_keys:
            # IRI total sales
            iri_sales = fact_sales[(fact_sales['Geography Key'] == iri_key) & 
                                  (fact_sales['Time Key'] == time_key)]['Value Sales'].sum()
            
            # Level 1 total
            level1_sales = fact_sales[(fact_sales['Geography Key'].isin(level1['geography_key'])) & 
                                     (fact_sales['Time Key'] == time_key)]['Value Sales'].sum()
            
            if iri_sales > 0 and level1_sales > 0:
                ratio = iri_sales / level1_sales
                
                if ratio < 2.3 or ratio > 2.7:  # Allow some tolerance around 2.5x
                    self.warnings.append(f"Period {time_key}: IRI/Level1 ratio = {ratio:.2f}x (target: 2.5x)")
                    hierarchy_valid = False
                else:
                    self.validation_results.append(f"✓ Period {time_key}: IRI/Level1 ratio = {ratio:.2f}x")
            
            # Check parent > children for each Level 1 store
            for _, parent_store in level1.iterrows():
                parent_key = parent_store['geography_key']
                parent_sales = fact_sales[(fact_sales['Geography Key'] == parent_key) & 
                                        (fact_sales['Time Key'] == time_key)]['Value Sales'].sum()
                
                # Get children
                children = geography[geography['parent_key'] == parent_key]
                if not children.empty:
                    children_sales = fact_sales[(fact_sales['Geography Key'].isin(children['geography_key'])) & 
                                              (fact_sales['Time Key'] == time_key)]['Value Sales'].sum()
                    
                    if children_sales > 0 and parent_sales <= children_sales:
                        self.errors.append(f"Period {time_key}, {parent_store['geography_description']}: "
                                         f"Parent sales ({parent_sales:.2f}) <= children ({children_sales:.2f})")
                        hierarchy_valid = False
        
        return hierarchy_valid
    
    def validate_temporal_consistency(self, fact_sales: pd.DataFrame, geography: pd.DataFrame, 
                                     products: pd.DataFrame) -> bool:
        """Validate month-on-month changes are within limits"""
        print("\n2. Validating Temporal Consistency...")
        
        # Sample some geography-brand combinations
        sample_geos = geography.sample(n=min(5, len(geography)))['geography_key'].tolist()
        
        # Get brands (approximate by manufacturer for simplicity)
        sample_brands = products['Manufacturer Value'].value_counts().head(10).index.tolist()
        
        temporal_valid = True
        
        for geo_key in sample_geos:
            for brand in sample_brands:
                # Get products for this brand
                brand_products = products[products['Manufacturer Value'] == brand]['Product Key'].tolist()
                
                # Get sales for this geo-brand combination
                brand_sales = fact_sales[(fact_sales['Geography Key'] == geo_key) & 
                                        (fact_sales['Product Key'].isin(brand_products))].copy()
                
                if len(brand_sales) < 2:
                    continue
                
                # Group by time and calculate total sales
                time_sales = brand_sales.groupby('Time Key')['Value Sales'].sum().reset_index()
                time_sales = time_sales.sort_values('Time Key')
                
                # Calculate period-on-period changes
                time_sales['MoM_Change'] = time_sales['Value Sales'].pct_change()
                
                # Check if changes are within ±2% for brand level
                large_changes = time_sales[abs(time_sales['MoM_Change']) > 0.02]
                if len(large_changes) > len(time_sales) * 0.2:  # Allow 20% of periods to exceed
                    self.warnings.append(f"Geo {geo_key}, Brand {brand}: "
                                       f"{len(large_changes)}/{len(time_sales)} periods exceed ±2% change")
                    temporal_valid = False
        
        # Check individual product changes (should be ±15%)
        sample_products = products.sample(n=min(20, len(products)))['Product Key'].tolist()
        
        for product_key in sample_products:
            product_sales = fact_sales[fact_sales['Product Key'] == product_key].copy()
            if len(product_sales) < 2:
                continue
            
            # Group by geography and time
            for geo_key in product_sales['Geography Key'].unique()[:3]:  # Check first 3 geos
                geo_product_sales = product_sales[product_sales['Geography Key'] == geo_key]
                time_sales = geo_product_sales.groupby('Time Key')['Value Sales'].sum().reset_index()
                time_sales = time_sales.sort_values('Time Key')
                time_sales['MoM_Change'] = time_sales['Value Sales'].pct_change()
                
                large_changes = time_sales[abs(time_sales['MoM_Change']) > 0.15]
                if len(large_changes) > len(time_sales) * 0.3:  # Allow 30% of periods to exceed
                    self.warnings.append(f"Product {product_key}, Geo {geo_key}: "
                                       f"Excessive MoM changes (>15%)")
        
        if temporal_valid:
            self.validation_results.append("✓ Temporal consistency validated")
        
        return temporal_valid
    
    def validate_brand_share(self, products: pd.DataFrame, fact_sales: pd.DataFrame) -> bool:
        """Validate Big Bite Chocolates market share is 4-10%"""
        print("\n3. Validating Brand Share Constraints...")
        
        # Find Big Bite products
        big_bite_products = products[
            products['Brand Value'].str.contains('BIG BITE', case=False, na=False)
        ]['Product Key'].tolist()
        
        if not big_bite_products:
            self.errors.append("No Big Bite Chocolate products found")
            return False
        
        brand_share_valid = True
        
        # Check each time period
        time_keys = fact_sales['Time Key'].unique()
        
        for time_key in time_keys[:20]:  # Check first 20 periods
            period_sales = fact_sales[fact_sales['Time Key'] == time_key]
            total_sales = period_sales['Value Sales'].sum()
            big_bite_sales = period_sales[period_sales['Product Key'].isin(big_bite_products)]['Value Sales'].sum()
            
            if total_sales > 0:
                market_share = (big_bite_sales / total_sales) * 100
                
                if market_share < 4.0 or market_share > 10.0:
                    self.warnings.append(f"Period {time_key}: Big Bite share = {market_share:.2f}% "
                                       f"(target: 4-10%)")
                    brand_share_valid = False
                else:
                    self.validation_results.append(f"✓ Period {time_key}: Big Bite share = {market_share:.2f}%")
        
        return brand_share_valid
    
    def validate_seasonal_patterns(self, products: pd.DataFrame, fact_sales: pd.DataFrame) -> bool:
        """Validate seasonal products have appropriate sales patterns"""
        print("\n4. Validating Seasonal Patterns...")
        
        # Find seasonal products
        christmas_products = products[
            products['Subsegment Value'].str.contains('CHRISTMAS|ADVENT', case=False, na=False)
        ]['Product Key'].tolist()
        
        easter_products = products[
            products['Subsegment Value'].str.contains('EASTER|EGG', case=False, na=False)
        ]['Product Key'].tolist()
        
        seasonal_valid = True
        
        # Check Christmas products (should peak in weeks 48-52)
        if christmas_products:
            christmas_sales = fact_sales[fact_sales['Product Key'].isin(christmas_products[:10])]
            
            # Group by week number (approximate)
            for product in christmas_products[:5]:  # Check first 5 products
                product_sales = christmas_sales[christmas_sales['Product Key'] == product]
                if product_sales.empty:
                    continue
                
                # Calculate week numbers
                product_sales['Week_Num'] = ((product_sales['Time Key'] - 2201) % 52) + 1
                
                # Check peak is in weeks 48-52
                peak_weeks = product_sales[product_sales['Week_Num'].between(48, 52)]
                off_season = product_sales[~product_sales['Week_Num'].between(44, 52)]
                
                if not peak_weeks.empty and not off_season.empty:
                    peak_avg = peak_weeks['Value Sales'].mean()
                    off_avg = off_season['Value Sales'].mean()
                    
                    if off_avg > 0:
                        ratio = peak_avg / off_avg
                        if ratio < 10:  # Peak should be at least 10x off-season
                            self.warnings.append(f"Christmas product {product}: "
                                               f"Insufficient seasonality (peak/off ratio: {ratio:.1f}x)")
                            seasonal_valid = False
        
        if seasonal_valid:
            self.validation_results.append("✓ Seasonal patterns validated")
        
        return seasonal_valid
    
    def validate_data_quality(self, fact_sales: pd.DataFrame) -> bool:
        """Validate data quality and consistency rules"""
        print("\n5. Validating Data Quality...")
        
        quality_valid = True
        
        # Check for negative values
        negative_sales = fact_sales[fact_sales['Value Sales'] < 0]
        if not negative_sales.empty:
            self.errors.append(f"Found {len(negative_sales)} records with negative sales")
            quality_valid = False
        
        # Check Value = Volume × Price relationship (approximate)
        sample = fact_sales.sample(n=min(1000, len(fact_sales)))
        for _, row in sample.iterrows():
            if pd.notna(row['Volume Sales']) and row['Volume Sales'] > 0:
                implied_price = row['Value Sales'] / row['Unit Sales'] if row['Unit Sales'] > 0 else 0
                if implied_price < 0.1 or implied_price > 1000:
                    self.warnings.append(f"Unrealistic implied price: ${implied_price:.2f}")
        
        # Check promotional sales <= total sales
        promo_cols = [col for col in fact_sales.columns if 'Price Cut' in col and 'Value' in col]
        for col in promo_cols:
            invalid = fact_sales[fact_sales[col] > fact_sales['Value Sales']]
            if not invalid.empty:
                self.errors.append(f"Promotional sales exceed total sales in {len(invalid)} records")
                quality_valid = False
        
        # Check column count
        if len(fact_sales.columns) != 188:
            self.warnings.append(f"Expected 188 columns, found {len(fact_sales.columns)}")
        else:
            self.validation_results.append("✓ Column count correct (188)")
        
        return quality_valid
    
    def run_validation(self):
        """Run all validations"""
        print("=" * 60)
        print("RGM Data Validation Report")
        print("=" * 60)
        
        # Load data
        products, geography, time, fact_sales = self.load_data()
        
        print(f"\nData Loaded:")
        print(f"  Products: {len(products):,} records")
        print(f"  Geography: {len(geography):,} locations")
        print(f"  Time: {len(time):,} periods")
        print(f"  Fact Sales: {len(fact_sales):,} records")
        
        # Run validations
        hierarchy_ok = self.validate_hierarchical_consistency(geography, fact_sales)
        temporal_ok = self.validate_temporal_consistency(fact_sales, geography, products)
        brand_ok = self.validate_brand_share(products, fact_sales)
        seasonal_ok = self.validate_seasonal_patterns(products, fact_sales)
        quality_ok = self.validate_data_quality(fact_sales)
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"\n✓ Successful Validations: {len(self.validation_results)}")
        for result in self.validation_results[:10]:
            print(f"  {result}")
        
        if self.warnings:
            print(f"\n⚠ Warnings: {len(self.warnings)}")
            for warning in self.warnings[:10]:
                print(f"  {warning}")
        
        if self.errors:
            print(f"\n✗ Errors: {len(self.errors)}")
            for error in self.errors[:10]:
                print(f"  {error}")
        
        # Overall result
        all_valid = hierarchy_ok and temporal_ok and brand_ok and seasonal_ok and quality_ok
        
        print("\n" + "=" * 60)
        if all_valid and not self.errors:
            print("RESULT: ✓ All constraints validated successfully")
        elif not self.errors:
            print("RESULT: ⚠ Validation passed with warnings")
        else:
            print("RESULT: ✗ Validation failed - constraints not met")
        print("=" * 60)
        
        return all_valid


if __name__ == "__main__":
    validator = DataValidator()
    validator.run_validation()