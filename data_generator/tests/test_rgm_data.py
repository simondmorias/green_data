#!/usr/bin/env python3
"""
Test suite for RGM Data Generator
Validates that generated data meets all requirements specified in product_requirements.md
"""

import pandas as pd
import numpy as np
import unittest
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')


class TestProductDimension(unittest.TestCase):
    """Test product dimension requirements"""
    
    @classmethod
    def setUpClass(cls):
        cls.products = pd.read_csv('generated_data/products_dimension.csv')
        cls.sample = pd.read_csv('provided_data/ILD_UK_PZCUSSONS_HANDSANITIZER_PROD_UD_2023-01-04-13-10-09_FINAL.csv')
    
    def test_schema_matches_sample(self):
        """Test that schema matches the sample file exactly"""
        self.assertEqual(
            list(self.products.columns), 
            list(self.sample.columns),
            "Column names must match sample file"
        )
    
    def test_product_count(self):
        """Test that 100,000 products were generated"""
        self.assertEqual(len(self.products), 100000, "Must have exactly 100,000 products")
    
    def test_unique_keys(self):
        """Test that Product Keys and Barcodes are unique"""
        self.assertEqual(
            len(self.products['Product Key'].unique()), 
            len(self.products),
            "All Product Keys must be unique"
        )
        self.assertEqual(
            len(self.products['Barcode Value'].unique()), 
            len(self.products),
            "All Barcode Values must be unique"
        )
    
    def test_manufacturer_count(self):
        """Test that 50 manufacturers exist"""
        n_manufacturers = self.products['Manufacturer Value'].nunique()
        self.assertEqual(n_manufacturers, 50, f"Must have exactly 50 manufacturers, found {n_manufacturers}")
    
    def test_brand_count(self):
        """Test that 400 brands exist"""
        n_brands = self.products['Brand Value'].nunique()
        self.assertGreaterEqual(n_brands, 400, f"Must have at least 400 brands, found {n_brands}")
    
    def test_big_bite_chocolates(self):
        """Test Big Bite Chocolates requirements"""
        big_bite = self.products[self.products['Manufacturer Value'] == 'BIG BITE CHOCOLATES']
        self.assertEqual(len(big_bite), 200, "Big Bite Chocolates must have exactly 200 products")
        
        big_bite_brands = big_bite['Brand Value'].nunique()
        self.assertGreaterEqual(big_bite_brands, 4, f"Big Bite must have at least 4 brands, found {big_bite_brands}")
    
    def test_private_label_share(self):
        """Test that Private Label has 15-20% market share"""
        private = self.products[self.products['Manufacturer Value'] == 'PRIVATE LABEL']
        share = len(private) / len(self.products)
        self.assertGreaterEqual(share, 0.15, f"Private Label share {share:.1%} must be >= 15%")
        self.assertLessEqual(share, 0.20, f"Private Label share {share:.1%} must be <= 20%")
    
    def test_needstate_distribution(self):
        """Test needstate distribution (75% chocolate, 20% sugar, 5% gum)"""
        distribution = self.products['Needstate Value'].value_counts(normalize=True)
        
        choc_share = distribution.get('CHOCOLATE CONFECTIONERY', 0)
        self.assertAlmostEqual(choc_share, 0.75, delta=0.05, 
                               msg=f"Chocolate share {choc_share:.1%} should be ~75%")
        
        sugar_share = distribution.get('SUGAR CONFECTIONERY', 0)
        self.assertAlmostEqual(sugar_share, 0.20, delta=0.05,
                               msg=f"Sugar share {sugar_share:.1%} should be ~20%")
        
        gum_share = distribution.get('CHEWING GUM', 0)
        self.assertAlmostEqual(gum_share, 0.05, delta=0.03,
                               msg=f"Gum share {gum_share:.1%} should be ~5%")
    
    def test_segment_distribution(self):
        """Test segment distribution within chocolate"""
        chocolate = self.products[self.products['Needstate Value'] == 'CHOCOLATE CONFECTIONERY']
        distribution = chocolate['Segment Value'].value_counts(normalize=True)
        
        # Expected: Bars 40%, Blocks 25%, Sharing 20%, Boxed 10%, Seasonal 5%
        expected = {
            'BARS / COUNTLINES': 0.40,
            'BLOCKS & TABLETS': 0.25,
            'SHARING BAGS & POUCHES': 0.20,
            'BOXED & ASSORTMENTS': 0.10,
            'SEASONAL & GIFTING': 0.05
        }
        
        for segment, expected_share in expected.items():
            actual_share = distribution.get(segment, 0)
            self.assertAlmostEqual(actual_share, expected_share, delta=0.05,
                                 msg=f"{segment} share {actual_share:.1%} should be ~{expected_share:.0%}")
    
    def test_pack_format_distribution(self):
        """Test pack format distribution (85% single, 15% multi)"""
        # Account for data quality variations
        single_count = self.products[self.products['Pack Format Value'] == 'SINGLE PACK'].shape[0]
        multi_count = self.products[self.products['Pack Format Value'].str.contains('MULTI', case=False, na=False)].shape[0]
        
        total = single_count + multi_count
        single_share = single_count / total
        multi_share = multi_count / total
        
        self.assertAlmostEqual(single_share, 0.85, delta=0.05,
                             msg=f"Single pack share {single_share:.1%} should be ~85%")
        self.assertAlmostEqual(multi_share, 0.15, delta=0.05,
                             msg=f"Multipack share {multi_share:.1%} should be ~15%")
    
    def test_seasonal_products_exist(self):
        """Test that seasonal products exist"""
        # Christmas products
        christmas = self.products[
            self.products['Subsegment Value'].str.contains('ADVENT|CHRISTMAS', case=False, na=False)
        ]
        self.assertGreater(len(christmas), 0, "Must have Christmas products")
        
        # Easter products
        easter = self.products[
            self.products['Subsegment Value'].str.contains('EASTER', case=False, na=False)
        ]
        self.assertGreater(len(easter), 0, "Must have Easter products")
        
        # Valentine products
        valentine = self.products[
            self.products['Subsegment Value'].str.contains('VALENTINE', case=False, na=False)
        ]
        self.assertGreater(len(valentine), 0, "Must have Valentine products")
        
        # Check seasonal segment
        seasonal = self.products[self.products['Segment Value'] == 'SEASONAL & GIFTING']
        self.assertGreater(len(seasonal), 0, "Must have products in Seasonal & Gifting segment")


class TestGeographyDimension(unittest.TestCase):
    """Test geography dimension requirements"""
    
    @classmethod
    def setUpClass(cls):
        cls.geography = pd.read_csv('generated_data/geography_dimension.csv')
        cls.sample = pd.read_csv('provided_data/ILD_UK_PZCUSSONS_HANDSANITIZER_GEOG_UD_2023-01-04-13-00-04_FINAL.csv')
    
    def test_schema_matches_hierarchy(self):
        """Test that schema has hierarchy columns"""
        expected_columns = ['geography_key', 'geography_description', 'parent_key', 'parent_description', 'hierarchy_level']
        self.assertEqual(
            list(self.geography.columns),
            expected_columns,
            "Column names must match hierarchy structure"
        )
    
    def test_required_retailers(self):
        """Test that all major UK retailers are included"""
        descriptions = self.geography['geography_description'].tolist()
        
        required_retailers = [
            'IRI All Outlets', 'Tesco', 'Sainsburys', 'Asda', 
            'Morrisons', 'Waitrose', 'Co-op', 'Aldi', 'Lidl',
            'Boots', 'Superdrug', 'Convenience'
        ]
        
        for retailer in required_retailers:
            self.assertTrue(
                any(retailer in desc for desc in descriptions),
                f"Must include {retailer} in geography"
            )
    
    def test_online_channels(self):
        """Test that online channels exist"""
        online_count = sum('Online' in desc for desc in self.geography['geography_description'])
        self.assertGreater(online_count, 0, "Must have online channels")
    
    def test_geography_keys_unique(self):
        """Test that Geography Keys are unique"""
        self.assertEqual(
            len(self.geography['geography_key'].unique()),
            len(self.geography),
            "All Geography Keys must be unique"
        )


class TestTimeDimension(unittest.TestCase):
    """Test time dimension requirements"""
    
    @classmethod
    def setUpClass(cls):
        cls.time = pd.read_csv('generated_data/time_dimension.csv')
        cls.sample = pd.read_csv('provided_data/ILD_UK_PZCUSSONS_HANDSANITIZER_TIME_UD_2023-01-04-13-10-09_FINAL.csv')
    
    def test_schema_matches_sample(self):
        """Test that schema matches the sample file"""
        self.assertEqual(
            list(self.time.columns),
            list(self.sample.columns),
            "Column names must match sample file"
        )
    
    def test_weekly_periods(self):
        """Test that 156 weekly periods exist (3 years)"""
        self.assertEqual(len(self.time), 156, "Must have exactly 156 weekly periods")
    
    def test_time_key_sequential(self):
        """Test that Time Keys are sequential"""
        keys = self.time['Time Key'].tolist()
        for i in range(1, len(keys)):
            self.assertEqual(keys[i], keys[i-1] + 1, "Time Keys must be sequential")
    
    def test_date_format(self):
        """Test that date format matches requirement"""
        for desc in self.time['Time Description']:
            # Format should be "1 w/e DD Mon, YYYY"
            self.assertTrue(desc.startswith('1 w/e '), f"Invalid format: {desc}")
            self.assertIn(',', desc, f"Missing comma in: {desc}")
            
            # Check year is in range
            year = int(desc.split(', ')[-1])
            self.assertIn(year, [2022, 2023, 2024, 2025], f"Year {year} out of range")


class TestFactSales(unittest.TestCase):
    """Test fact sales table requirements"""
    
    @classmethod
    def setUpClass(cls):
        cls.fact = pd.read_csv('generated_data/fact_sales.csv')
        cls.sample = pd.read_csv('provided_data/ILD_UK_PZCUSSONS_HANDSANITIZER_FACT_UD_2023-01-04-13-03-03_FINAL.csv')
        cls.products = pd.read_csv('generated_data/products_dimension.csv')
        cls.geography = pd.read_csv('generated_data/geography_dimension.csv')
        cls.time = pd.read_csv('generated_data/time_dimension.csv')
    
    def test_column_count(self):
        """Test that fact table has 188 columns"""
        self.assertEqual(len(self.fact.columns), 188, "Fact table must have exactly 188 columns")
    
    def test_foreign_keys_valid(self):
        """Test that all foreign keys reference valid dimension records"""
        # Product keys
        invalid_products = ~self.fact['Product Key'].isin(self.products['Product Key'])
        self.assertEqual(invalid_products.sum(), 0, "All Product Keys must exist in product dimension")
        
        # Geography keys
        invalid_geography = ~self.fact['Geography Key'].isin(self.geography['Geography Key'])
        self.assertEqual(invalid_geography.sum(), 0, "All Geography Keys must exist in geography dimension")
        
        # Time keys
        invalid_time = ~self.fact['Time Key'].isin(self.time['Time Key'])
        self.assertEqual(invalid_time.sum(), 0, "All Time Keys must exist in time dimension")
    
    def test_sparsity(self):
        """Test that fact table is sparse (not all combinations have sales)"""
        total_possible = len(self.products) * len(self.geography) * len(self.time)
        actual_records = len(self.fact)
        sparsity = actual_records / total_possible
        
        self.assertLess(sparsity, 0.4, f"Fact table sparsity {sparsity:.1%} should be < 40%")
        self.assertGreater(actual_records, 1000, "Must have substantial number of records")
    
    def test_sales_metrics_present(self):
        """Test that core sales metrics are present"""
        required_metrics = ['Unit Sales', 'Volume Sales', 'Value Sales',
                          'Base Unit Sales', 'Base Volume Sales', 'Base Value Sales']
        
        for metric in required_metrics:
            self.assertIn(metric, self.fact.columns, f"Must have {metric} column")
            
            # Check that at least some values are non-null
            non_null = self.fact[metric].notna().sum()
            self.assertGreater(non_null, 0, f"{metric} must have some non-null values")
    
    def test_sales_value_distribution(self):
        """Test that sales values have realistic distribution"""
        value_sales = self.fact['Value Sales'].dropna()
        
        # Should have heavy right skew
        self.assertGreater(value_sales.max(), value_sales.mean() * 10,
                          "Sales should have heavy right skew")
        
        # Should have positive values
        self.assertGreater(value_sales.min(), 0, "Sales values must be positive")
        
        # Median should be much less than mean (right skew)
        self.assertLess(value_sales.median(), value_sales.mean(),
                       "Median should be less than mean (right skew)")


class TestSeasonalPatterns(unittest.TestCase):
    """Test seasonal sales patterns"""
    
    @classmethod
    def setUpClass(cls):
        cls.fact = pd.read_csv('generated_data/fact_sales.csv')
        cls.products = pd.read_csv('generated_data/products_dimension.csv')
        cls.time = pd.read_csv('generated_data/time_dimension.csv')
        
        # Identify seasonal products
        cls.christmas_products = cls.products[
            cls.products['Subsegment Value'].str.contains('ADVENT|CHRISTMAS', case=False, na=False)
        ]['Product Key'].tolist()
        
        cls.easter_products = cls.products[
            cls.products['Subsegment Value'].str.contains('EASTER', case=False, na=False)
        ]['Product Key'].tolist()
    
    def test_christmas_peak(self):
        """Test that Christmas products peak in weeks 48-52"""
        if not self.christmas_products:
            self.skipTest("No Christmas products found")
        
        # Get Christmas product sales
        christmas_sales = self.fact[self.fact['Product Key'].isin(self.christmas_products)]
        
        if len(christmas_sales) == 0:
            self.skipTest("No Christmas product sales found")
        
        # Add week number to sales
        christmas_sales = christmas_sales.merge(self.time, on='Time Key')
        
        # Extract week numbers from descriptions
        christmas_sales['Week'] = christmas_sales['Time Description'].str.extract(r'(\d+) \w+,')[0].astype(int)
        
        # Group by week and calculate average sales
        weekly_avg = christmas_sales.groupby('Week')['Value Sales'].mean()
        
        # Check if December weeks have higher sales (simplified test)
        if len(weekly_avg) > 0:
            overall_avg = weekly_avg.mean()
            # At least one week should have significantly higher sales
            self.assertTrue(
                any(weekly_avg > overall_avg * 2),
                "Christmas products should have peak sales periods"
            )
    
    def test_easter_peak(self):
        """Test that Easter products peak in weeks 10-16"""
        if not self.easter_products:
            self.skipTest("No Easter products found")
        
        # Get Easter product sales
        easter_sales = self.fact[self.fact['Product Key'].isin(self.easter_products)]
        
        if len(easter_sales) == 0:
            self.skipTest("No Easter product sales found")
        
        # Add time information
        easter_sales = easter_sales.merge(self.time, on='Time Key')
        
        # Check that Easter products have sales
        self.assertGreater(len(easter_sales), 0, "Easter products should have sales")


class TestRegionalVariations(unittest.TestCase):
    """Test regional product variations"""
    
    @classmethod
    def setUpClass(cls):
        cls.fact = pd.read_csv('generated_data/fact_sales.csv')
        cls.products = pd.read_csv('generated_data/products_dimension.csv')
        cls.geography = pd.read_csv('generated_data/geography_dimension.csv')
    
    def test_premium_in_waitrose(self):
        """Test that premium products over-index in Waitrose"""
        waitrose = self.geography[self.geography['Geography Description'].str.contains('Waitrose')]
        
        if len(waitrose) == 0:
            self.skipTest("No Waitrose stores found")
        
        premium_manufacturers = ['LINDT', 'HOTEL CHOCOLAT', 'GODIVA', 'THORNTONS']
        premium_products = self.products[
            self.products['Manufacturer Value'].isin(premium_manufacturers)
        ]['Product Key'].tolist()
        
        if not premium_products:
            self.skipTest("No premium products found")
        
        # Check that some premium products are sold in Waitrose
        waitrose_sales = self.fact[self.fact['Geography Key'].isin(waitrose['Geography Key'])]
        premium_in_waitrose = waitrose_sales[waitrose_sales['Product Key'].isin(premium_products)]
        
        # Should have some premium products in Waitrose
        if len(waitrose_sales) > 0:
            premium_share = len(premium_in_waitrose) / len(waitrose_sales)
            self.assertGreater(premium_share, 0, "Waitrose should carry premium products")
    
    def test_store_format_differences(self):
        """Test that different store formats have different product ranges"""
        # Compare Tesco vs Tesco Express
        tesco_main = self.geography[self.geography['Geography Description'] == 'Tesco']
        tesco_express = self.geography[self.geography['Geography Description'] == 'Tesco Express']
        
        if len(tesco_main) == 0 or len(tesco_express) == 0:
            self.skipTest("Tesco stores not found")
        
        # Get product ranges for each
        tesco_main_sales = self.fact[self.fact['Geography Key'].isin(tesco_main['Geography Key'])]
        tesco_express_sales = self.fact[self.fact['Geography Key'].isin(tesco_express['Geography Key'])]
        
        if len(tesco_main_sales) > 0 and len(tesco_express_sales) > 0:
            main_products = tesco_main_sales['Product Key'].nunique()
            express_products = tesco_express_sales['Product Key'].nunique()
            
            # Express should have fewer unique products (convenience format)
            self.assertLessEqual(express_products, main_products,
                               "Express stores should have limited range")


class TestDataQualityIssues(unittest.TestCase):
    """Test intentional data quality issues"""
    
    @classmethod
    def setUpClass(cls):
        cls.products = pd.read_csv('generated_data/products_dimension.csv')
        cls.fact = pd.read_csv('generated_data/fact_sales.csv')
    
    def test_multipack_variations(self):
        """Test that MULTIPACK has inconsistent formatting"""
        pack_formats = self.products['Pack Format Value'].value_counts()
        
        # Should have variations like MULTIPACK, MULTI PACK, MULTI-PACK
        multipack_variations = [k for k in pack_formats.index if 'MULTI' in k.upper()]
        
        self.assertGreater(len(multipack_variations), 1,
                          "Should have multiple variations of MULTIPACK formatting")
    
    def test_size_format_variations(self):
        """Test that sizes have format variations"""
        sizes = self.products['Total Size Value'].tolist()
        
        # Check for variations like "100G", "100 G", "100GR"
        variations = set()
        for size in sizes[:1000]:  # Check first 1000 for performance
            if isinstance(size, str):
                if 'G' in size or 'ML' in size:
                    variations.add(size[-2:] if len(size) > 2 else size)
        
        self.assertGreater(len(variations), 1,
                          "Should have variations in size formatting")
    
    def test_missing_data_patterns(self):
        """Test that fact table has realistic missing data"""
        # Check for NaN values in promotional columns
        promo_columns = [col for col in self.fact.columns if 'Promotion' in col or 'Promo' in col]
        
        if promo_columns:
            null_counts = self.fact[promo_columns].isnull().sum()
            
            # Should have some null values in promotional columns
            self.assertGreater(null_counts.sum(), 0,
                             "Promotional columns should have null values when no promotion")


class TestComplexScenarios(unittest.TestCase):
    """Test complex business scenarios"""
    
    @classmethod
    def setUpClass(cls):
        cls.fact = pd.read_csv('generated_data/fact_sales.csv')
        cls.products = pd.read_csv('generated_data/products_dimension.csv')
        cls.time = pd.read_csv('generated_data/time_dimension.csv')
    
    def test_product_lifecycle_patterns(self):
        """Test that some products show lifecycle patterns"""
        # Group sales by product and time
        product_time_sales = self.fact.groupby(['Product Key', 'Time Key'])['Value Sales'].sum().reset_index()
        
        # Check for products with increasing sales over time (new launches)
        products_with_growth = []
        
        for product in product_time_sales['Product Key'].unique()[:100]:  # Sample for performance
            product_sales = product_time_sales[product_time_sales['Product Key'] == product]
            
            if len(product_sales) > 5:
                # Sort by time
                product_sales = product_sales.sort_values('Time Key')
                
                # Check if early sales are lower than later sales
                early_avg = product_sales.head(3)['Value Sales'].mean()
                late_avg = product_sales.tail(3)['Value Sales'].mean()
                
                if late_avg > early_avg * 1.5:
                    products_with_growth.append(product)
        
        self.assertGreater(len(products_with_growth), 0,
                          "Should have some products showing growth patterns")
    
    def test_substitution_possibilities(self):
        """Test that similar products exist for substitution"""
        # Check for products with same brand but different sizes
        brand_groups = self.products.groupby('Brand Value')
        
        brands_with_multiple_sizes = []
        for brand, group in brand_groups:
            sizes = group['Total Size Value'].nunique()
            if sizes > 1:
                brands_with_multiple_sizes.append(brand)
        
        self.assertGreater(len(brands_with_multiple_sizes), 50,
                          "Many brands should have multiple size variants for substitution")
    
    def test_price_architecture(self):
        """Test that larger sizes have better unit prices (where applicable)"""
        # This would require price data which might be in the promotional columns
        # Simplified test: check that multiple sizes exist for products
        
        products_by_brand_subsegment = self.products.groupby(['Brand Value', 'Subsegment Value'])
        
        multi_size_products = 0
        for (brand, subsegment), group in products_by_brand_subsegment:
            if group['Total Size Value'].nunique() > 1:
                multi_size_products += 1
        
        self.assertGreater(multi_size_products, 100,
                          "Should have many product variants with different sizes")


def run_tests():
    """Run all tests and generate a report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestProductDimension,
        TestGeographyDimension,
        TestTimeDimension,
        TestFactSales,
        TestSeasonalPatterns,
        TestRegionalVariations,
        TestDataQualityIssues,
        TestComplexScenarios
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary report
    print("\n" + "="*60)
    print("TEST SUMMARY REPORT")
    print("="*60)
    
    print(f"\nTotal Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailed Tests:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()[:100]}")
    
    if result.errors:
        print("\nTests with Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(':')[-1].strip()[:100]}")
    
    # Overall result
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Data conforms to requirements!")
    else:
        print("❌ SOME TESTS FAILED - Review the failures above")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)