# RGM Data Query Guide

## Overview

This guide provides instructions and example SQL queries for analyzing the Retail Grocery Merchandise (RGM) data generated for the UK confectionery market. The data models sales patterns, seasonal variations, and complex retail scenarios across 100K products and 3 years of weekly sales data.

## Data Model Structure

### Dimension Tables

1. **DimProduct** (`DimProduct`)
   - Primary Key: `product_key`
   - Hierarchy: Manufacturer → Brand → SubBrand → Segment →  SubSegment → Product
   - Key columns: `manufacturer_value`, `brand_value`, `owner`
   - Owner types: 'Ours' (Big Bite Chocolates), 'Private Label', 'Competitor'

2. **DimGeography** (`generated_data/DimGeography.csv`)
   - Primary Key: `geography_key`
   - Hierarchy Levels:
     - Level 1: IRI All Outlets (total market)
     - Level 2: Major Retailers (e.g., Tesco, ASDA, Sainsbury's)
     - Level 3: Retail Channels (e.g., Online, Express, Superstores)
   - Key columns: `hierarchy_level`, `parent_key`

3. **DimDate** (`generated_data/DimDate.csv`)
   - Primary Key: `time_key`
   - Granularity: Weekly (ending on Sundays)
   - Key columns: `week_ending_date`, `year`, `week_number`, `seasonal_period`

### Fact Table

**Fact_Sales** (`generated_data_small/fact_sales.csv`)
- Foreign Keys: `geography_key`, `product_key`, `time_key`
- Core Measures:
  - `value_sales`: Total sales value (£)
  - `volume_sales`: Total volume sold
  - `unit_sales`: Total units sold
  - `base_value_sales`: Non-promotional sales value
  - `stores_selling`: Number of stores with sales
  - `price_per_unit`: Average selling price

## Critical Query Rules

### ⚠️ MANDATORY: Geography Filtering Rules

**EVERY query MUST include a geography filter and NEVER mix hierarchy levels:**

```sql
-- ✅ CORRECT: Query at Level 0 (Total Market)
WHERE g.hierarchy_level = 0
  AND g.geography_description = 'IRI All Outlets'

-- ✅ CORRECT: Query at Level 1 (Specific Retailer)
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'Tesco'

-- ❌ WRONG: Mixing levels or no filter
-- This will cause double-counting!
```

**Default**: If no geography is specified, use Level 1 'IRI All Outlets'

### Our Products Definition

"Our" products are defined as:
- `manufacturer_value = 'BIG BITE CHOCOLATES'` OR
- `owner = 'Ours'`

## Common Query Patterns

### 1. Basic Sales Query (Total Market)

```sql
-- Weekly sales for our products at total market level
SELECT 
    d.week_ending_date,
    SUM(f.value_sales) as total_value,
    SUM(f.volume_sales) as total_volume,
    SUM(f.unit_sales) as total_units
FROM fact_sales f
JOIN DimDate d ON f.time_key = d.time_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimProduct p ON f.product_key = p.product_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND p.owner = 'Ours'
  AND d.week_ending_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY d.week_ending_date
ORDER BY d.week_ending_date;
```

### 2. Market Share Calculation

```sql
-- Market share by manufacturer using window function
SELECT 
    p.manufacturer_value,
    SUM(f.value_sales) as manufacturer_sales,
    SUM(SUM(f.value_sales)) OVER () as total_market_sales,
    (SUM(f.value_sales) / SUM(SUM(f.value_sales)) OVER () * 100) as market_share_pct
FROM fact_sales f
JOIN DimDate d ON f.time_key = d.time_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimProduct p ON f.product_key = p.product_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND d.year = 2024
GROUP BY p.manufacturer_value
ORDER BY market_share_pct DESC;

-- Or for just our market share with additional context
SELECT 
    p.owner,
    SUM(f.value_sales) as sales,
    SUM(SUM(f.value_sales)) OVER () as total_market,
    (SUM(f.value_sales) / SUM(SUM(f.value_sales)) OVER () * 100) as market_share_pct,
    RANK() OVER (ORDER BY SUM(f.value_sales) DESC) as market_position
FROM fact_sales f
JOIN DimDate d ON f.time_key = d.time_key
JOIN DimGeography g ON f.geography_key = g.geography_key  
JOIN DimProduct p ON f.product_key = p.product_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND d.year = 2024
GROUP BY p.owner
ORDER BY sales DESC;
```

### 3. Retailer Performance Comparison

```sql
-- Our performance by major retailer
SELECT 
    g.geography_description as retailer,
    SUM(f.value_sales) as total_sales,
    SUM(f.stores_selling) as stores_with_sales,
    AVG(f.price_per_unit) as avg_price
FROM fact_sales f
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimProduct p ON f.product_key = p.product_key
JOIN DimDate d ON f.time_key = d.time_key
WHERE g.hierarchy_level = 2  -- Retailer level
  AND p.owner = 'Ours'
  AND d.year = 2024
GROUP BY g.geography_description
ORDER BY total_sales DESC;
```

### 4. Seasonal Analysis

```sql
-- Christmas vs Normal period sales comparison
SELECT 
    d.seasonal_period,
    COUNT(DISTINCT d.week_ending_date) as weeks,
    SUM(f.value_sales) as total_sales,
    SUM(f.value_sales) / COUNT(DISTINCT d.week_ending_date) as avg_weekly_sales
FROM fact_sales f
JOIN DimDate d ON f.time_key = d.time_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimProduct p ON f.product_key = p.product_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND p.owner = 'Ours'
  AND d.year = 2024
  AND d.seasonal_period IN ('Christmas', 'Normal')
GROUP BY d.seasonal_period;
```

### 5. Product Performance Ranking

```sql
-- Top 10 performing products by value
SELECT 
    p.product_description,
    p.brand_value,
    p.size_group_value,
    SUM(f.value_sales) as total_sales,
    SUM(f.unit_sales) as units_sold,
    AVG(f.price_per_unit) as avg_price
FROM fact_sales f
JOIN DimProduct p ON f.product_key = p.product_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimDate d ON f.time_key = d.time_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND p.owner = 'Ours'
  AND d.year = 2024
GROUP BY p.product_key, p.product_description, p.brand_value, p.size_group_value
ORDER BY total_sales DESC
LIMIT 10;
```

### 6. Promotional Effectiveness

```sql
-- Promotional vs Non-promotional sales analysis
SELECT 
    p.brand_value,
    SUM(f.value_sales) as total_sales,
    SUM(f.base_value_sales) as base_sales,
    SUM(f.value_sales - f.base_value_sales) as incremental_sales,
    ((SUM(f.value_sales) - SUM(f.base_value_sales)) / SUM(f.value_sales) * 100) as promo_contribution_pct
FROM fact_sales f
JOIN DimProduct p ON f.product_key = p.product_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimDate d ON f.time_key = d.time_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND p.owner = 'Ours'
  AND d.year = 2024
GROUP BY p.brand_value
HAVING SUM(f.value_sales) > 0
ORDER BY total_sales DESC;
```

### 7. Channel Performance (Level 3)

```sql
-- Performance by retail channel within Tesco
SELECT 
    g.geography_description as channel,
    SUM(f.value_sales) as total_sales,
    SUM(f.volume_sales) as total_volume,
    COUNT(DISTINCT f.product_key) as products_sold
FROM fact_sales f
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimProduct p ON f.product_key = p.product_key
JOIN DimDate d ON f.time_key = d.time_key
WHERE g.hierarchy_level = 3
  AND g.parent_description = 'Tesco'
  AND p.owner = 'Ours'
  AND d.year = 2024
GROUP BY g.geography_description
ORDER BY total_sales DESC;
```

### 8. Year-over-Year Growth

```sql
-- YoY growth comparison
WITH yearly_sales AS (
    SELECT 
        d.year,
        SUM(f.value_sales) as annual_sales
    FROM fact_sales f
    JOIN DimDate d ON f.time_key = d.time_key
    JOIN DimGeography g ON f.geography_key = g.geography_key
    JOIN DimProduct p ON f.product_key = p.product_key
    WHERE g.hierarchy_level = 1 
      AND g.geography_description = 'IRI All Outlets'
      AND p.owner = 'Ours'
    GROUP BY d.year
)
SELECT 
    curr.year,
    curr.annual_sales as current_year_sales,
    prev.annual_sales as previous_year_sales,
    ((curr.annual_sales - prev.annual_sales) / prev.annual_sales * 100) as yoy_growth_pct
FROM yearly_sales curr
LEFT JOIN yearly_sales prev ON curr.year = prev.year + 1
ORDER BY curr.year;
```

### 9. Distribution Analysis

```sql
-- Product distribution across stores
SELECT 
    p.brand_value,
    COUNT(DISTINCT f.product_key) as num_products,
    AVG(f.stores_selling) as avg_stores_selling,
    MAX(f.stores_selling) as max_distribution,
    AVG(f.tdp) as avg_tdp,  -- Total Distribution Points
    AVG(f.acv) as avg_acv   -- All Commodity Volume
FROM fact_sales f
JOIN DimProduct p ON f.product_key = p.product_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimDate d ON f.time_key = d.time_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND p.owner = 'Ours'
  AND d.year = 2024
  AND d.week_number = 26  -- Mid-year snapshot
GROUP BY p.brand_value
ORDER BY avg_stores_selling DESC;
```

### 10. Competitor Comparison

```sql
-- Our performance vs competitors by category
SELECT 
    p.category_value,
    p.owner,
    SUM(f.value_sales) as total_sales,
    COUNT(DISTINCT p.product_key) as product_count,
    AVG(f.price_per_unit) as avg_price
FROM fact_sales f
JOIN DimProduct p ON f.product_key = p.product_key
JOIN DimGeography g ON f.geography_key = g.geography_key
JOIN DimDate d ON f.time_key = d.time_key
WHERE g.hierarchy_level = 1 
  AND g.geography_description = 'IRI All Outlets'
  AND d.year = 2024
  AND p.category_value = 'Chocolate'
GROUP BY p.category_value, p.owner
ORDER BY p.category_value, total_sales DESC;
```

## Key Metrics Definitions

| Metric | Description | Calculation |
|--------|-------------|-------------|
| Market Share | % of total market sales | (Our Sales / Total Market Sales) × 100 |
| Distribution | Store presence | stores_selling / total_stores |
| Rate of Sale | Sales velocity | value_sales / stores_selling |
| Promotional Lift | Incremental from promotions | (value_sales - base_value_sales) / base_value_sales |
| Price per Unit | Average selling price | value_sales / unit_sales |
| TDP | Total Distribution Points | Weighted distribution measure |
| ACV | All Commodity Volume | % of market covered by distribution |

## Performance Tips

1. **Always filter geography first** to avoid scanning unnecessary data
2. **Use appropriate time ranges** - data spans 2022-2024
3. **Join dimensions before fact table** for better query plans
4. **Aggregate at appropriate levels** - don't query Level 3 when Level 2 suffices
5. **Use CTEs for complex calculations** like market share

## Common Pitfalls to Avoid

❌ **Don't mix geography hierarchy levels** - causes double counting
❌ **Don't forget week_ending_date filter** - 3 years of weekly data is large
❌ **Don't sum across all geographies** without filtering by level
❌ **Don't assume all products have sales** - matrix is sparse (~40% populated)
❌ **Don't ignore the owner field** when analyzing "our" products

