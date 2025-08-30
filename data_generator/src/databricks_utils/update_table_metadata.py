#!/usr/bin/env python3
"""
Update Unity Catalog table metadata for RGM chocolate sales data
"""

import subprocess
import json
import pandas as pd

def execute_sql(sql, warehouse_id="04beb8e364a0cc53"):
    """Execute SQL statement using databricks CLI"""
    cmd = [
        "databricks", "warehouses", "execute",
        warehouse_id,
        "--sql", sql,
        "--profile", "rgm_poc"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing SQL: {e.stderr}")
        return None

def update_time_dimension():
    """Update metadata for time_dimension table"""
    print("Updating time_dimension table metadata...")
    
    # Update table comment
    sql = """
    ALTER TABLE rgm_poc.chocolate.time_dimension 
    SET TBLPROPERTIES ('comment' = 'Weekly time dimension table for retail chocolate sales analysis. Contains week-ending dates from 2022-2024 for time series analysis.')
    """
    execute_sql(sql)
    
    # Update column comments
    column_updates = [
        ("time_key", "Unique identifier for each week (format: YYWW where YY=year, WW=week number)"),
        ("time_description", "Human-readable week ending date description (format: 'w/e DD Mon, YYYY')")
    ]
    
    for col_name, comment in column_updates:
        sql = f"""
        ALTER TABLE rgm_poc.chocolate.time_dimension 
        ALTER COLUMN {col_name} 
        COMMENT '{comment}'
        """
        execute_sql(sql)
    
    print("✓ time_dimension metadata updated")

def update_geography_dimension():
    """Update metadata for geography_dimension table"""
    print("Updating geography_dimension table metadata...")
    
    # Update table comment
    sql = """
    ALTER TABLE rgm_poc.chocolate.geography_dimension 
    SET TBLPROPERTIES ('comment' = 'Geographic hierarchy for UK retail outlets. Contains store chains, online channels, and aggregated market views for chocolate sales analysis.')
    """
    execute_sql(sql)
    
    # Update column comments
    column_updates = [
        ("geography_key", "Unique 8-digit identifier for each geographic entity (store/chain/market)"),
        ("geography_description", "Name of the retail outlet, chain, or market aggregation level")
    ]
    
    for col_name, comment in column_updates:
        sql = f"""
        ALTER TABLE rgm_poc.chocolate.geography_dimension 
        ALTER COLUMN {col_name} 
        COMMENT '{comment}'
        """
        execute_sql(sql)
    
    print("✓ geography_dimension metadata updated")

def update_products_dimension():
    """Update metadata for products_dimension table"""
    print("Updating products_dimension table metadata...")
    
    # Update table comment
    sql = """
    ALTER TABLE rgm_poc.chocolate.products_dimension 
    SET TBLPROPERTIES ('comment' = 'Product master data for chocolate confectionery items. Contains detailed product attributes including brand hierarchy, pack formats, and flavor variants from major manufacturers.')
    """
    execute_sql(sql)
    
    # Update column comments
    column_updates = [
        ("product_key", "Unique product identifier (9-10 digit integer)"),
        ("product_description", "Full product description including brand, variant, flavor, and size"),
        ("barcode_value", "EAN-13 barcode for product identification at point of sale"),
        ("category_value", "Top-level product category (CONFECTIONERY)"),
        ("needstate_value", "Consumer need category (e.g., CHOCOLATE CONFECTIONERY)"),
        ("segment_value", "Product format segment (e.g., BARS/COUNTLINES, BLOCKS & TABLETS)"),
        ("subsegment_value", "Detailed product type within segment"),
        ("manufacturer_value", "Parent company/manufacturer name"),
        ("brand_value", "Primary brand name"),
        ("subbrand_value", "Sub-brand or product line variant"),
        ("fragrance_value", "Flavor/variant description (e.g., MILK CHOCOLATE, DARK CHOCOLATE)"),
        ("total_size_value", "Package size with unit of measure"),
        ("size_group_value", "Size category for analysis (e.g., SHARE PACK, FAMILY PACK)"),
        ("pack_format_value", "Single or multi-pack indicator"),
        ("special_pack_type_value", "Promotional or seasonal pack type indicator")
    ]
    
    for col_name, comment in column_updates:
        sql = f"""
        ALTER TABLE rgm_poc.chocolate.products_dimension 
        ALTER COLUMN {col_name} 
        COMMENT '{comment}'
        """
        execute_sql(sql)
    
    print("✓ products_dimension metadata updated")

def update_fact_sales():
    """Update metadata for fact_sales table"""
    print("Updating fact_sales table metadata...")
    
    # Update table comment
    sql = """
    ALTER TABLE rgm_poc.chocolate.fact_sales 
    SET TBLPROPERTIES ('comment' = 'Fact table containing weekly retail sales metrics for chocolate products. Includes value, volume, unit sales with extensive promotional and distribution metrics.')
    """
    execute_sql(sql)
    
    # Key column comments - focusing on most important metrics
    column_updates = [
        ("geography_key", "Foreign key to geography_dimension"),
        ("product_key", "Foreign key to products_dimension"),
        ("time_key", "Foreign key to time_dimension"),
        ("value_sales", "Total sales value in GBP"),
        ("volume_sales", "Total volume sold (units depend on product)"),
        ("unit_sales", "Total number of units sold"),
        ("base_value_sales", "Baseline sales value excluding promotions"),
        ("base_volume_sales", "Baseline volume excluding promotions"),
        ("base_unit_sales", "Baseline units excluding promotions"),
        ("store_count", "Total number of stores in geography"),
        ("stores_selling", "Number of stores with sales for this product"),
        ("value_sales_price_cut", "Sales value from price reduction promotions"),
        ("volume_sales_price_cut", "Volume sold under price reduction"),
        ("value_sales_special_pack", "Sales value from special pack promotions"),
        ("volume_sales_special_pack", "Volume sold as special packs"),
        ("value_sales_on_shelf", "Sales value from on-shelf promotions"),
        ("volume_sales_on_shelf", "Volume sold with on-shelf promotions"),
        ("value_sales_off_shelf", "Sales value from off-shelf displays"),
        ("volume_sales_off_shelf", "Volume sold from off-shelf displays"),
        ("value_sales_no_promotion", "Sales value without any promotions"),
        ("volume_sales_no_promotion", "Volume sold without promotions"),
        ("tdp", "Total Distribution Points - % of stores carrying product"),
        ("acv", "All Commodity Volume - % of total market sales coverage"),
        ("price_per_unit", "Average price per unit sold"),
        ("base_price_per_unit", "Regular price per unit (non-promotional)")
    ]
    
    for col_name, comment in column_updates:
        sql = f"""
        ALTER TABLE rgm_poc.chocolate.fact_sales 
        ALTER COLUMN {col_name} 
        COMMENT '{comment}'
        """
        execute_sql(sql)
    
    print("✓ fact_sales metadata updated")

def main():
    """Main execution"""
    print("Starting Unity Catalog metadata update for RGM chocolate sales data...")
    print("=" * 60)
    
    update_time_dimension()
    update_geography_dimension()
    update_products_dimension()
    update_fact_sales()
    
    print("=" * 60)
    print("✅ All table metadata successfully updated!")

if __name__ == "__main__":
    main()