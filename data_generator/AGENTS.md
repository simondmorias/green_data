# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RGM Data Generator - A comprehensive tool for generating realistic retail grocery merchandise (RGM) data with complex patterns and scenarios for data science teams to test analytical capabilities. The project focuses on UK confectionery market data with realistic sales patterns, seasonal variations, and deliberate complexity.

## Key Commands

```bash
# Generate full dataset (100K products, 3 years of sales data)
python3 generate_rgm_data.py

# Run tests to validate data meets requirements
python3 test_rgm_data.py

# Check generated data quality
python3 check_data.py

# Update Databricks table metadata
python3 update_table_metadata.py
python3 update_metadata_sdk.py
```

## Architecture

The project generates four interconnected dimensional datasets:

1. **Products Dimension** (`products_dimension.csv`) - 100K products with realistic hierarchy
2. **Geography Dimension** (`geography_dimension.csv`) - UK retail channels and stores  
3. **Time Dimension** (`time_dimension.csv`) - Weekly periods covering 3 years
4. **Fact Sales** (`fact_sales.csv`) - Sparse sales matrix with 188 metrics

### Core Generator Structure

- `ProductDimensionGenerator`: Creates manufacturer → brand → product hierarchy with realistic market shares
- `GeographyDimensionGenerator`: Models UK retail landscape (supermarkets, discounters, convenience, online)
- `TimeDimensionGenerator`: Weekly time periods with bank holiday awareness
- `FactSalesGenerator`: Complex sales patterns including seasonality, promotions, cannibalization

### Data Complexity Features

The generator embeds deliberate test scenarios:
- Seasonal patterns (Christmas 3.5-5x baseline, Easter 2.5-4x)
- Product lifecycle scenarios (launches, delistings, replacements)
- Regional variations (size variants by geography)
- Supply chain disruptions (erratic availability patterns)
- Cannibalization effects (new products impacting existing)
- Viral product spikes (500% sudden increases)
- Data quality issues (5% barcode changes, description inconsistencies)

## Sample Data Schema

Sample files in `provided_data/` define the required schema:

|File Pattern|Description|Key Columns|
|----|----|----| 
|*_FACT_UD_*.csv|Fact Sales|188 columns including sales metrics, promotional data|
|*_GEOG_UD_*.csv|Geography|Geography Key, Geography Description|
|*_PROD_UD_*.csv|Products|15 columns defining product hierarchy|
|*_TIME_UD_*.csv|Time|Time Key, Time Description|

## Dependencies

- Python 3.12+
- pandas 2.3.1 - Data manipulation and CSV I/O
- numpy 2.3.2 - Numerical operations and distributions
- No external data sources required (all synthetic generation)

## Critical Implementation Details

### Market Share Distribution
- Top 5 manufacturers control 40% of market
- Private label is largest single "manufacturer" at 18%
- Power law distribution for brand product counts

### Sales Realism Rules
- Value = Volume × Price per unit (enforced)
- Only ~40% of product/geography/time combinations have sales (sparse matrix)
- Promotional sales ≤ Total sales
- Base sales + Incremental sales = Total sales

### Special Requirements
- Big Bite Chocolates: Must have exactly 4 brands, 15 product ranges, 200 products
- Seasonal products: 5% of total, concentrated in specific weeks
- Price architecture: Non-linear pricing by size to encourage trade-up