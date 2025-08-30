try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import (
        col, row_number, current_timestamp, lit, 
        when, monotonically_increasing_id, dense_rank
    )
    from pyspark.sql.window import Window
except ImportError:
    print("Note: PySpark packages will be available in Databricks environment")
    print("For local development, install with: pip install -r requirements.txt")
    import sys
    sys.exit(1)


def main():
    """
    Create master_product_hierarchy table with two hierarchical structures:
    1. Brand hierarchy:
       - Level 0: Manufacturer
       - Level 1: Brand (child of Manufacturer)
    2. Category hierarchy:
       - Level 0: Category
       - Level 1: Needstate (child of Category)
       - Level 2: Segment (child of Needstate)
       - Level 3: Subsegment (child of Segment)
    """
    
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("Create Master Product Hierarchy Table") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
    
    print("Starting master_product_hierarchy table creation...")
    
    try:
        # Read dimproduct table
        dimproduct_df = spark.table("rgm_poc.chocolate.dimproduct")
        print(f"Successfully read dimproduct table")
        
        # ========== BRAND HIERARCHY ==========
        # Level 0: Get distinct manufacturers
        manufacturers_df = dimproduct_df.select("manufacturer_value").distinct() \
            .withColumn("hierarchy_name", lit("Brand")) \
            .withColumn("level", lit(0)) \
            .withColumn("parent_key", lit(None).cast("long")) \
            .withColumnRenamed("manufacturer_value", "description")
        
        # Assign product_hierarchy_key to manufacturers
        window_spec = Window.orderBy("description")
        manufacturers_with_key = manufacturers_df \
            .withColumn("product_hierarchy_key", row_number().over(window_spec))
        
        print(f"Found {manufacturers_with_key.count()} distinct manufacturers")
        
        # Level 1: Get distinct manufacturer-brand combinations
        brands_df = dimproduct_df.select("manufacturer_value", "brand_value").distinct()
        
        # Join with manufacturers to get parent keys
        brands_with_parent = brands_df.join(
            manufacturers_with_key.select("description", "product_hierarchy_key"),
            brands_df.manufacturer_value == manufacturers_with_key.description,
            "inner"
        ).select(
            col("brand_value").alias("description"),
            col("product_hierarchy_key").alias("parent_key"),
            "manufacturer_value"
        ).withColumn("hierarchy_name", lit("Brand")) \
         .withColumn("level", lit(1))
        
        # Assign product_hierarchy_key to brands (continuing from manufacturer keys)
        max_manufacturer_key = manufacturers_with_key.agg({"product_hierarchy_key": "max"}).collect()[0][0]
        window_spec_brands = Window.orderBy("description")
        brands_with_key = brands_with_parent \
            .withColumn("product_hierarchy_key", 
                       row_number().over(window_spec_brands) + lit(max_manufacturer_key))
        
        print(f"Found {brands_with_key.count()} distinct brands")
        
        # Combine Brand hierarchy levels
        brand_hierarchy_df = manufacturers_with_key.select(
            "product_hierarchy_key", "hierarchy_name", "level", 
            "parent_key", "description"
        ).union(
            brands_with_key.select(
                "product_hierarchy_key", "hierarchy_name", "level", 
                "parent_key", "description"
            )
        )
        
        # ========== CATEGORY HIERARCHY ==========
        # Get the max key from Brand hierarchy to continue numbering
        max_brand_hierarchy_key = brand_hierarchy_df.agg({"product_hierarchy_key": "max"}).collect()[0][0]
        
        # Level 0: Get distinct categories
        categories_df = dimproduct_df.select("category_value").distinct() \
            .withColumn("hierarchy_name", lit("Category")) \
            .withColumn("level", lit(0)) \
            .withColumn("parent_key", lit(None).cast("long")) \
            .withColumnRenamed("category_value", "description")
        
        window_spec_cat = Window.orderBy("description")
        categories_with_key = categories_df \
            .withColumn("product_hierarchy_key", 
                       row_number().over(window_spec_cat) + lit(max_brand_hierarchy_key))
        
        print(f"Found {categories_with_key.count()} distinct categories")
        
        # Level 1: Get distinct category-needstate combinations
        needstates_df = dimproduct_df.select("category_value", "needstate_value").distinct()
        
        needstates_with_parent = needstates_df.join(
            categories_with_key.select("description", "product_hierarchy_key"),
            needstates_df.category_value == categories_with_key.description,
            "inner"
        ).select(
            col("needstate_value").alias("description"),
            col("product_hierarchy_key").alias("parent_key"),
            "category_value"
        ).withColumn("hierarchy_name", lit("Category")) \
         .withColumn("level", lit(1))
        
        max_category_key = categories_with_key.agg({"product_hierarchy_key": "max"}).collect()[0][0]
        window_spec_need = Window.orderBy("description")
        needstates_with_key = needstates_with_parent \
            .withColumn("product_hierarchy_key", 
                       row_number().over(window_spec_need) + lit(max_category_key))
        
        print(f"Found {needstates_with_key.count()} distinct needstates")
        
        # Level 2: Get distinct needstate-segment combinations
        segments_df = dimproduct_df.select("needstate_value", "segment_value").distinct()
        
        segments_with_parent = segments_df.join(
            needstates_with_key.select("description", "product_hierarchy_key"),
            segments_df.needstate_value == needstates_with_key.description,
            "inner"
        ).select(
            col("segment_value").alias("description"),
            col("product_hierarchy_key").alias("parent_key"),
            "needstate_value"
        ).withColumn("hierarchy_name", lit("Category")) \
         .withColumn("level", lit(2))
        
        max_needstate_key = needstates_with_key.agg({"product_hierarchy_key": "max"}).collect()[0][0]
        window_spec_seg = Window.orderBy("description")
        segments_with_key = segments_with_parent \
            .withColumn("product_hierarchy_key", 
                       row_number().over(window_spec_seg) + lit(max_needstate_key))
        
        print(f"Found {segments_with_key.count()} distinct segments")
        
        # Level 3: Get distinct segment-subsegment combinations
        subsegments_df = dimproduct_df.select("segment_value", "subsegment_value").distinct()
        
        subsegments_with_parent = subsegments_df.join(
            segments_with_key.select("description", "product_hierarchy_key"),
            subsegments_df.segment_value == segments_with_key.description,
            "inner"
        ).select(
            col("subsegment_value").alias("description"),
            col("product_hierarchy_key").alias("parent_key"),
            "segment_value"
        ).withColumn("hierarchy_name", lit("Category")) \
         .withColumn("level", lit(3))
        
        max_segment_key = segments_with_key.agg({"product_hierarchy_key": "max"}).collect()[0][0]
        window_spec_subseg = Window.orderBy("description")
        subsegments_with_key = subsegments_with_parent \
            .withColumn("product_hierarchy_key", 
                       row_number().over(window_spec_subseg) + lit(max_segment_key))
        
        print(f"Found {subsegments_with_key.count()} distinct subsegments")
        
        # Combine Category hierarchy levels
        category_hierarchy_df = categories_with_key.select(
            "product_hierarchy_key", "hierarchy_name", "level", 
            "parent_key", "description"
        ).union(
            needstates_with_key.select(
                "product_hierarchy_key", "hierarchy_name", "level", 
                "parent_key", "description"
            )
        ).union(
            segments_with_key.select(
                "product_hierarchy_key", "hierarchy_name", "level", 
                "parent_key", "description"
            )
        ).union(
            subsegments_with_key.select(
                "product_hierarchy_key", "hierarchy_name", "level", 
                "parent_key", "description"
            )
        )
        
        # Combine both hierarchies
        hierarchy_df = brand_hierarchy_df.union(category_hierarchy_df)
        
        # Add created_at timestamp
        final_hierarchy_df = hierarchy_df \
            .withColumn("created_at", current_timestamp()) \
            .select("product_hierarchy_key", "hierarchy_name", "level", 
                   "parent_key", "description", "created_at") \
            .orderBy("product_hierarchy_key")
        
        # Display sample data
        print("\nSample of Brand hierarchy:")
        print("\nLevel 0 (Manufacturers):")
        final_hierarchy_df.filter((col("hierarchy_name") == "Brand") & (col("level") == 0)).show(5, truncate=False)
        
        print("\nLevel 1 (Brands):")
        final_hierarchy_df.filter((col("hierarchy_name") == "Brand") & (col("level") == 1)).show(5, truncate=False)
        
        print("\nSample of Category hierarchy:")
        print("\nLevel 0 (Categories):")
        final_hierarchy_df.filter((col("hierarchy_name") == "Category") & (col("level") == 0)).show(3, truncate=False)
        
        print("\nLevel 1 (Needstates):")
        final_hierarchy_df.filter((col("hierarchy_name") == "Category") & (col("level") == 1)).show(3, truncate=False)
        
        print("\nLevel 2 (Segments):")
        final_hierarchy_df.filter((col("hierarchy_name") == "Category") & (col("level") == 2)).show(3, truncate=False)
        
        print("\nLevel 3 (Subsegments):")
        final_hierarchy_df.filter((col("hierarchy_name") == "Category") & (col("level") == 3)).show(3, truncate=False)
        
        # Write to new table
        final_hierarchy_df.write \
            .mode("overwrite") \
            .saveAsTable("rgm_poc.chocolate.master_product_hierarchy")
        
        print(f"\nSuccessfully created rgm_poc.chocolate.master_product_hierarchy table")
        print(f"Total records written: {final_hierarchy_df.count()}")
        
        # Display summary by hierarchy and level
        hierarchy_summary = final_hierarchy_df.groupBy("hierarchy_name", "level").count().orderBy("hierarchy_name", "level")
        print("\nRecords by hierarchy and level:")
        hierarchy_summary.show()
        
        # Verify the table was created
        verification_df = spark.table("rgm_poc.chocolate.master_product_hierarchy")
        print(f"\nVerification - Table row count: {verification_df.count()}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    
    finally:
        # Gracefully close Spark session
        try:
            spark.stop()
            print("\nSpark session closed")
        except Exception:
            # Session might already be closed by Databricks Connect
            pass


if __name__ == "__main__":
    main()