#!/usr/bin/env python3
"""
Generate SQL statements to update Unity Catalog table metadata
"""

def generate_sql_statements():
    """Generate SQL ALTER statements for updating table metadata"""
    
    catalog = "rgm_poc"
    schema = "chocolate"
    
    sql_statements = []
    
    # Time dimension metadata (DimDate table)
    sql_statements.append(f"""
-- Update DimDate table and columns (Time Dimension)
COMMENT ON TABLE {catalog}.{schema}.DimDate IS 
'Weekly time dimension table for retail chocolate sales analysis. Contains week-ending dates from 2022-2025 with full temporal attributes.';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN time_key 
COMMENT 'Unique identifier for each week (format: YYWW where YY=last 2 digits of year, WW=week number)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN time_description 
COMMENT 'Human-readable week ending date description (format: 1 w/e DD Mon, YYYY)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN week_ending_date 
COMMENT 'Week ending date in YYYY-MM-DD format (Saturday)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN year 
COMMENT 'Year as 2-digit integer (22 for 2022, etc.)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN week_number 
COMMENT 'ISO week number (1-52)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN quarter 
COMMENT 'Quarter of the year (Q1, Q2, Q3, Q4)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN year_quarter 
COMMENT 'Year and quarter combination (YY-QN format)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN month 
COMMENT 'Month number (1-12)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN month_name 
COMMENT 'Full month name (January, February, etc.)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN month_short 
COMMENT '3-letter month abbreviation (Jan, Feb, etc.)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN year_month 
COMMENT 'Year-month combination (YYYY-MM format)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN week_start_date 
COMMENT 'Week start date in YYYY-MM-DD format (Sunday)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN fiscal_year 
COMMENT 'UK fiscal year as 2-digit integer (April-March)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN fiscal_year_label 
COMMENT 'Fiscal year label (FYxx format)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN seasonal_period 
COMMENT 'Seasonal sales period (Christmas Period, Easter Period, Summer Period, Halloween Period, Back to School, Regular Period)';

ALTER TABLE {catalog}.{schema}.DimDate ALTER COLUMN relative_period 
COMMENT 'Relative time period for analysis (Current Week, Previous Week, Previous Month, Previous Quarter, Older, Future)';
""")
    
    # Geography dimension metadata (DimGeography table)
    sql_statements.append(f"""
-- Update DimGeography table and columns (Geography Dimension)
COMMENT ON TABLE {catalog}.{schema}.DimGeography IS 
'Geographic hierarchy for UK retail outlets. Contains store chains, online channels, and aggregated market views with parent-child relationships.';

ALTER TABLE {catalog}.{schema}.DimGeography ALTER COLUMN geography_key 
COMMENT 'Unique 8-digit identifier for each geographic entity (store/chain/market)';

ALTER TABLE {catalog}.{schema}.DimGeography ALTER COLUMN geography_description 
COMMENT 'Name of the retail outlet, chain, or market aggregation level';

ALTER TABLE {catalog}.{schema}.DimGeography ALTER COLUMN parent_key 
COMMENT 'Foreign key to parent geography entity for hierarchy navigation';

ALTER TABLE {catalog}.{schema}.DimGeography ALTER COLUMN parent_description 
COMMENT 'Name of the parent geography entity';

ALTER TABLE {catalog}.{schema}.DimGeography ALTER COLUMN hierarchy_level 
COMMENT 'Level in geography hierarchy (0=Top/All Outlets, 1=Retailer, 2=Store Format/Online)';
""")
    
    # Products dimension metadata (DimProduct table)
    sql_statements.append(f"""
-- Update DimProduct table and columns (Product Dimension)
COMMENT ON TABLE {catalog}.{schema}.DimProduct IS 
'Product master data for confectionery. Contains 100K products with brand hierarchy, pack formats, and flavor variants.';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN product_key 
COMMENT 'Unique product identifier (9-10 digit integer)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN product_description 
COMMENT 'Full product description including brand, variant, flavor, and size';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN barcode_value 
COMMENT 'EAN-13 barcode for POS identification (12-digit)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN category_value 
COMMENT 'Top-level product category (CONFECTIONERY)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN needstate_value 
COMMENT 'Consumer need category (CHOCOLATE CONFECTIONERY, SUGAR CONFECTIONERY, CHEWING GUM)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN segment_value 
COMMENT 'Product format segment (BARS / COUNTLINES, BLOCKS & TABLETS, SHARING BAGS & POUCHES, BOXED & ASSORTMENTS, SEASONAL & GIFTING)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN subsegment_value 
COMMENT 'Detailed product type within segment (SOLID, FILLED, WAFER, MILK, DARK, WHITE, etc.)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN manufacturer_value 
COMMENT 'Parent company/manufacturer name (50+ manufacturers including NESTLE, MARS, LINDT, FERRERO, PRIVATE LABEL)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN brand_value 
COMMENT 'Primary brand name (400+ unique brands from real UK market data)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN subbrand_value 
COMMENT 'Sub-brand or product line variant';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN fragrance_value 
COMMENT 'Flavor/variant description (MILK CHOCOLATE, DARK CHOCOLATE 70%, WHITE CHOCOLATE, CARAMEL, MINT, etc.)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN total_size_value 
COMMENT 'Package size with unit of measure (e.g., 45G, 100G, 4 X 35G for multipacks)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN size_group_value 
COMMENT 'Size category for analysis (SINGLE-SERVE <60G, SHARE PACK 60-150G, FAMILY PACK 150-300G, GIFT/SEASONAL >300G, MULTIPACK 4-12 UNITS)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN pack_format_value 
COMMENT 'Single or multi-pack indicator (SINGLE PACK, MULTIPACK)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN special_pack_type_value 
COMMENT 'Promotional or seasonal pack indicator (NON SPECIAL PACK, PMP, NOT APPLICABLE)';

ALTER TABLE {catalog}.{schema}.DimProduct ALTER COLUMN owner 
COMMENT 'Ownership indicator (Ours for Big Bite Chocolates products, Competitor for all others)';
""")
    
    # Fact sales metadata (FactSales table)
    sql_statements.append(f"""
-- Update FactSales table
COMMENT ON TABLE {catalog}.{schema}.FactSales IS 
'Weekly retail sales metrics for confectionery products from 2022-2025. Contains 188 columns including value, volume, units with promotional breakdowns and distribution metrics. Sparse matrix with ~40% of product/geography/time combinations having sales.';

-- Core dimension keys (columns 1-3)
ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN geography_key 
COMMENT 'Foreign key to DimGeography (8-digit store/chain identifier)';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN product_key 
COMMENT 'Foreign key to DimProduct (9-10 digit product identifier)';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN time_key 
COMMENT 'Foreign key to DimDate (YYWW format)';

-- Core sales metrics (columns 4-10)
ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales 
COMMENT 'Total sales value in GBP';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN unit_sales 
COMMENT 'Total number of units sold';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN volume_sales 
COMMENT 'Total volume sold (weight varies by product pack size)';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN base_value_sales 
COMMENT 'Baseline sales value excluding all promotions';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN base_unit_sales 
COMMENT 'Baseline units excluding all promotions';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN store_count 
COMMENT 'Total number of stores in geography';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN stores_selling 
COMMENT 'Number of stores with sales for this product';

-- Promotional sales columns (columns 11-118) - examples
ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_No_Promotion 
COMMENT 'Sales value with no promotional activity';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_Price_Cut_Only 
COMMENT 'Sales value from price cut promotions only';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_Special_Pack_Only 
COMMENT 'Sales value from special pack promotions only';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_On_Shelf 
COMMENT 'Sales value from on-shelf promotions';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_Off_Shelf 
COMMENT 'Sales value from off-shelf displays';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_Gondola_End 
COMMENT 'Sales value from gondola end displays';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_sales_Secondary_Display 
COMMENT 'Sales value from secondary display locations';

-- Rate of sale columns (examples)
ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN value_rate_of_sale_No_Promotion 
COMMENT 'Value sales rate per store per week with no promotion';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN unit_rate_of_sale_Price_Cut_Only 
COMMENT 'Unit sales rate per store per week with price cuts';

-- Distribution metrics (columns 179-188)
ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Total_Distribution 
COMMENT 'Total distribution points across all stores';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Numeric_Distribution 
COMMENT 'Number of stores stocking the product';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Weighted_Distribution 
COMMENT 'Sales-weighted distribution percentage';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Average_Items_Stocked 
COMMENT 'Average number of items stocked per store';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Average_Items_Sold 
COMMENT 'Average number of items sold per store';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Stock_Cover_Days 
COMMENT 'Days of stock coverage based on current sales rate';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN Forward_Stock_Cover 
COMMENT 'Forward-looking stock coverage in days';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN OOS_Instances 
COMMENT 'Number of out-of-stock instances';

ALTER TABLE {catalog}.{schema}.FactSales ALTER COLUMN OOS_Duration 
COMMENT 'Average duration of out-of-stock periods in days';
""")
    
    # Write all SQL to file
    with open("update_metadata.sql", "w") as f:
        f.write("-- SQL statements to update Unity Catalog metadata for RGM chocolate sales tables\n")
        f.write("-- Execute these in Databricks SQL Editor or Notebook\n\n")
        for sql in sql_statements:
            f.write(sql)
            f.write("\n")
    
    print("SQL statements generated in update_metadata.sql")
    print("\nTo apply these updates:")
    print("1. Open Databricks SQL Editor or a Notebook")
    print("2. Connect to the SQL warehouse")
    print("3. Copy and execute the SQL statements from update_metadata.sql")
    
    # Also print summary statistics
    print("\n" + "="*60)
    print("DATA SUMMARY FOR UNITY CATALOG METADATA:")
    print("="*60)
    
    print("\n📊 DIMDATE (Time Dimension - 208 rows)")
    print("  - Period: Weekly data from Jan 2022 to Dec 2025")
    print("  - Format: Week-ending dates (Saturday)")
    print("  - Temporal attributes: Year, Quarter, Month, Week, Fiscal Year")
    print("  - Seasonal periods: Christmas, Easter, Summer, Halloween, Back to School")
    
    print("\n🏪 DIMGEOGRAPHY (Geography Dimension - 35 rows)")
    print("  - Coverage: UK retail market with 3-level hierarchy")
    print("  - Level 0: IRI All Outlets (market total)")
    print("  - Level 1: Major retailers (Tesco, ASDA, Sainsbury's, Morrisons, etc.)")
    print("  - Level 2: Store formats and online channels")
    print("  - Includes: Discounters (Aldi, Lidl), Convenience, Online")
    
    print("\n🍫 DIMPRODUCT (Product Dimension - 100,000 rows)")
    print("  - Category: Confectionery (Chocolate, Sugar, Gum)")
    print("  - Manufacturers: 50+ including NESTLE, MARS, LINDT, FERRERO, PRIVATE LABEL")
    print("  - Brands: 400+ real UK market brands from provided data")
    print("  - Segments: Bars/Countlines, Blocks/Tablets, Sharing Bags, Boxed, Seasonal")
    print("  - Sizes: Single-serve to gift packs, including multipacks")
    print("  - Special: Big Bite Chocolates (200 products, 4 brands, 15 ranges)")
    
    print("\n💰 FACTSALES")
    print("  - Table: FactSales (single table containing all years 2022-2025)")
    print("  - Grain: Weekly sales by product by geography")
    print("  - Sparsity: ~40% of possible combinations have sales (realistic)")
    print("  - Columns: 188 total including:")
    print("    • Core metrics: value_sales, volume_sales, unit_sales")
    print("    • Base metrics: base_value_sales, base_unit_sales")
    print("    • Promotional breakdowns: 18 promo types × 6 metrics = 108 columns")
    print("    • Rate of sale metrics: per store per week calculations")
    print("    • Distribution metrics: TDP, ACV, stock coverage, OOS tracking")
    print("  - Embedded patterns: Seasonality, viral spikes, cannibalization, lifecycle")

if __name__ == "__main__":
    generate_sql_statements()