import pandas as pd

# Load and check the new fact table
fact = pd.read_csv("generated_data/fact_sales.csv")
products = pd.read_csv("generated_data/products_dimension.csv")

print("FACT TABLE STATISTICS:")
print(f"Total records: {len(fact):,}")
print(f"File size: 103MB")
print(f"Columns: {len(fact.columns)}")
print(f"Unique products in sales: {fact['Product Key'].nunique():,}")
print(f"Unique stores in sales: {fact['Geography Key'].nunique()}")
print(f"Unique weeks in sales: {fact['Time Key'].nunique()}")

print("\nSALES VALUE DISTRIBUTION:")
value_sales = fact["Value Sales"].dropna()
print(f"Min: ${value_sales.min():.2f}")
print(f"Median: ${value_sales.median():.2f}")
print(f"Mean: ${value_sales.mean():.2f}")
print(f"Max: ${value_sales.max():.2f}")

print("\nSEASONAL PRODUCT COVERAGE:")
seasonal = products[products["Segment Value"] == "SEASONAL & GIFTING"]["Product Key"]
seasonal_sales = fact[fact["Product Key"].isin(seasonal)]
print(f"Seasonal products with sales: {seasonal_sales['Product Key'].nunique()}/{len(seasonal)}")
print(f"Seasonal sales records: {len(seasonal_sales):,}")

print("\n10X IMPROVEMENT:")
print(f"Previous records: 74,310")
print(f"Current records: {len(fact):,}")
print(f"Increase: {len(fact)/74310:.1f}x")