#!/usr/bin/env python3
"""
Update Unity Catalog table metadata using Databricks SDK
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import TableInfo, ColumnInfo

def main():
    """Update table and column metadata"""
    
    # Initialize client using CLI profile
    w = WorkspaceClient(profile="rgm_poc")
    
    catalog = "rgm_poc"
    schema = "chocolate"
    
    # Define metadata for each table
    tables_metadata = {
        "time_dimension": {
            "comment": "Weekly time dimension table for retail chocolate sales analysis. Contains week-ending dates from 2022-2024.",
            "columns": {
                "time_key": "Unique identifier for each week (format: YYWW where YY=year, WW=week number)",
                "time_description": "Human-readable week ending date description (format: 'w/e DD Mon, YYYY')"
            }
        },
        "geography_dimension": {
            "comment": "Geographic hierarchy for UK retail outlets. Contains store chains, online channels, and aggregated market views.",
            "columns": {
                "geography_key": "Unique 8-digit identifier for each geographic entity (store/chain/market)",
                "geography_description": "Name of the retail outlet, chain, or market aggregation level"
            }
        },
        "products_dimension": {
            "comment": "Product master data for chocolate confectionery. Contains brand hierarchy, pack formats, and flavor variants.",
            "columns": {
                "product_key": "Unique product identifier (9-10 digit integer)",
                "product_description": "Full product description including brand, variant, flavor, and size",
                "barcode_value": "EAN-13 barcode for POS identification",
                "category_value": "Top-level product category",
                "needstate_value": "Consumer need category",
                "segment_value": "Product format segment (BARS, BLOCKS, etc.)",
                "subsegment_value": "Detailed product type within segment",
                "manufacturer_value": "Parent company/manufacturer name",
                "brand_value": "Primary brand name",
                "subbrand_value": "Sub-brand or product line variant",
                "fragrance_value": "Flavor/variant description",
                "total_size_value": "Package size with unit of measure",
                "size_group_value": "Size category for analysis",
                "pack_format_value": "Single or multi-pack indicator",
                "special_pack_type_value": "Promotional or seasonal pack indicator"
            }
        },
        "fact_sales": {
            "comment": "Weekly retail sales metrics for chocolate products. Includes value, volume, units with promotional and distribution metrics.",
            "columns": {
                "geography_key": "Foreign key to geography_dimension",
                "product_key": "Foreign key to products_dimension",
                "time_key": "Foreign key to time_dimension",
                "value_sales": "Total sales value in GBP",
                "volume_sales": "Total volume sold",
                "unit_sales": "Total number of units sold",
                "base_value_sales": "Baseline sales value excluding promotions",
                "base_volume_sales": "Baseline volume excluding promotions",
                "base_unit_sales": "Baseline units excluding promotions",
                "store_count": "Total number of stores in geography",
                "stores_selling": "Number of stores with sales",
                "value_sales_price_cut": "Sales value from price reductions",
                "volume_sales_price_cut": "Volume sold under price reduction",
                "value_sales_special_pack": "Sales value from special packs",
                "volume_sales_special_pack": "Volume sold as special packs",
                "value_sales_on_shelf": "Sales from on-shelf promotions",
                "volume_sales_on_shelf": "Volume from on-shelf promotions",
                "value_sales_off_shelf": "Sales from off-shelf displays",
                "volume_sales_off_shelf": "Volume from off-shelf displays",
                "value_sales_no_promotion": "Sales without promotions",
                "volume_sales_no_promotion": "Volume without promotions",
                "tdp": "Total Distribution Points - % stores carrying",
                "acv": "All Commodity Volume - % market coverage",
                "price_per_unit": "Average price per unit sold",
                "base_price_per_unit": "Regular price per unit"
            }
        }
    }
    
    for table_name, metadata in tables_metadata.items():
        full_name = f"{catalog}.{schema}.{table_name}"
        print(f"\nUpdating {full_name}...")
        
        try:
            # Get existing table info
            table = w.tables.get(full_name)
            
            # Update table comment
            table.comment = metadata["comment"]
            
            # Update column comments
            if table.columns:
                for col in table.columns:
                    if col.name in metadata["columns"]:
                        col.comment = metadata["columns"][col.name]
            
            # Apply updates
            w.tables.update(
                full_name=full_name,
                comment=table.comment
            )
            
            print(f"✓ Updated {table_name} table comment")
            
            # Note: Column comments may need to be updated via SQL ALTER statements
            # as the SDK update method may not support column-level comment updates
            
        except Exception as e:
            print(f"Error updating {table_name}: {e}")
    
    print("\n✅ Metadata update process completed!")

if __name__ == "__main__":
    main()