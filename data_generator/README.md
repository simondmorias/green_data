# RGM Data Generator - Statistical Models and Business Rules

## Overview

The RGM Data Generator creates realistic retail grocery merchandise data with complex patterns, hierarchical constraints, and temporal consistency. This system generates 100,000+ products across 34 geographic locations with 156 weeks of sales data, embedding realistic market dynamics and test scenarios for data science teams.

## Quick Start

```bash
# Generate full dataset
python3 generate_rgm_data.py

# Validate constraints are met
python3 validate_constraints.py

# Run tests
python3 test_rgm_data.py
```

## Data Architecture

### Dimensional Model
- **Products Dimension**: 100,000 products with 15-level hierarchy
- **Geography Dimension**: 34 locations in 3-level hierarchy
- **Time Dimension**: 156 weekly periods (3 years)
- **Fact Sales**: Sparse matrix with 188 metrics per record

## Statistical Models

### 1. Hierarchical Geography Model

The geography dimension follows a strict parent-child hierarchy with aggregation rules:

```
Level 0: IRI All Outlets (aggregate)
    ├── Level 1: Retail Chains (Tesco, Asda, Boots, etc.)
    │   └── Level 2: Sub-formats (Online, Express, Local, etc.)
```

**Aggregation Rules:**
- **IRI All Outlets** = 2.5× sum of Level 1 retailers
- **Each Level 1 retailer** > sum of its Level 2 children
- **Online channels** typically 10-30% of parent retailer

**Implementation:**
```python
class HierarchicalSalesModel:
    - Top-down generation starting from IRI total
    - Distributes 40% of IRI sales to Level 1
    - Allocates 30-70% of retailer sales to Level 2
    - Uses log-normal distribution with store-type parameters
```

### 2. Temporal Consistency Model

Sales follow autoregressive AR(1) patterns for realistic time series:

**AR(1) Model:** `sales(t) = α + β × sales(t-1) + ε`

**Parameters by Aggregation Level:**
| Level | β Range | MoM Change | Description |
|-------|---------|------------|-------------|
| Geography-Brand | 0.98-1.02 | ±2% | Stable aggregate trends |
| Individual Product | 0.85-1.15 | ±15% | Higher product-level volatility |

**Smoothing Formula:**
```python
smoothed_sales = 0.7 × AR_prediction + 0.3 × base_sales
```

### 3. Brand Share Constraints

**Big Bite Chocolates Market Share:**
- Target: 4-10% of total market each period
- 4 brands: Original, Deluxe, Crunch, Velvet
- 15 product ranges, 200 total SKUs
- Automatic adjustment to maintain share targets

**Enforcement Algorithm:**
1. Calculate current period market share
2. If outside 4-10% range, calculate adjustment factor
3. Scale Big Bite sales proportionally
4. Maintain relative brand strengths

### 4. Seasonal Patterns

Seasonal products follow smooth bell curves centered on peak weeks:

| Season | Peak Week | Peak Multiplier | Season Weeks | Off-Season |
|--------|-----------|-----------------|--------------|------------|
| Christmas | 51 | 5.0× | 44-52 | 0.1× |
| Easter | 14 | 4.0× | 10-16 | 0.05× |
| Valentine | 6 | 2.5× | 5-7 | 0.1× |

**Regular Product Seasonality:**
- Christmas weeks (48-52): 1.1-1.3× baseline
- Easter weeks (10-16): 1.2-1.4× baseline
- Summer weeks (26-35): 0.7-0.8× baseline

### 5. Price Elasticity Model

Volume response to price changes follows economic elasticity:

**Elasticity Ranges:**
| Product Type | Elasticity | Description |
|--------------|------------|-------------|
| Premium | -0.6 to -0.4 | Less price sensitive |
| Standard | -1.2 to -0.8 | Moderate sensitivity |
| Value | -1.5 to -1.2 | Highly price sensitive |

**Volume Calculation:**
```
Volume_change% = Elasticity × Price_change%
New_volume = Base_volume × (1 + Volume_change% / 100)
```

## Sales Distribution Parameters

### Log-Normal Distribution by Store Type

| Store Type | Mean (μ) | Std Dev (σ) | Min | Max |
|------------|----------|-------------|-----|-----|
| IRI All Outlets | 6.0 | 2.5 | 10 | 100,000 |
| Premium (Waitrose) | 5.5 | 2.0 | 5 | 50,000 |
| Major Chains | 5.0 | 2.2 | 2 | 40,000 |
| Discounters | 4.5 | 2.3 | 1 | 30,000 |
| Convenience | 3.5 | 1.8 | 0.5 | 10,000 |
| Online | 4.0 | 2.0 | 1 | 20,000 |

## Business Rules

### Product Distribution Rules

1. **Premium Products** (Lindt, Godiva, Hotel Chocolat):
   - 90% availability in Waitrose
   - 10% availability in discounters
   - Higher price points ($15-50)

2. **Private Label Products**:
   - Only sold in own-brand stores
   - Cannot appear in competitor retailers
   - Value pricing ($1-5)

3. **Convenience Stores**:
   - Stock only top 20% of SKUs
   - Limited seasonal space
   - Higher prices (+25% vs supermarkets)

### Data Quality Constraints

1. **Value Consistency**:
   - Value Sales = Volume × Price per unit
   - Promotional sales ≤ Total sales
   - Base sales + Incremental = Total sales

2. **Sparsity**:
   - ~40% of product/geography/time combinations have sales
   - Seasonal products: <10% availability outside season
   - Regional products: Limited geographic distribution

3. **Temporal Stability**:
   - No sudden jumps >50% without promotion
   - Smooth transitions between periods
   - Consistent week-over-week patterns

## Embedded Test Scenarios

### 1. Cannibalization Detection
- Snickers Ice Cream launches Week 20
- Regular Snickers drops 15% in freezer-adjacent stores
- Stronger effect in convenience (-20%) vs supermarkets (-10%)

### 2. Viral Product Effect
- Pistachio Kunafa Chocolate (Dubai trend)
- Week 5: +500% spike from TikTok
- Weeks 6-8: Stock-outs
- Weeks 9-12: Declining -20% per week

### 3. Supply Chain Disruption
- Ferrero products Weeks 30-33
- Week 31: 40% store availability
- Week 32: 60% store availability
- Competitor premium +35% in affected stores

### 4. Shrinkflation Pattern
- Products reduce size maintaining price
- Example: Yorkie 50g → 46g at Week 21
- -5% unit sales (consumer awareness)
- New barcode for smaller size

## Validation Checks

Run `python3 validate_constraints.py` to verify:

1. **Hierarchical Consistency**
   - IRI = 2.5× Level 1 sum (±10% tolerance)
   - Parent > children for all geographies

2. **Temporal Consistency**
   - Geography-Brand MoM within ±2%
   - Product MoM within ±15%

3. **Brand Share**
   - Big Bite Chocolates 4-10% each period
   - Consistent relative brand strengths

4. **Seasonal Patterns**
   - Peak sales in appropriate weeks
   - Minimal off-season sales

5. **Data Quality**
   - No negative values
   - Realistic price ranges
   - 188 columns in fact table

## File Structure

```
rgm_data_generator/
├── generate_rgm_data.py       # Main generator with dimension builders
├── statistical_models.py      # Statistical modeling classes
├── validate_constraints.py    # Constraint validation script
├── test_rgm_data.py          # Unit tests
├── product_requirements.md    # Detailed requirements
├── CLAUDE.md                 # AI assistant instructions
├── generated_data/           # Output directory
│   ├── products_dimension.csv
│   ├── geography_dimension.csv
│   ├── time_dimension.csv
│   └── fact_sales.csv
└── provided_data/            # Sample data files
```

## Advanced Usage

### Adjusting Market Parameters

```python
# In statistical_models.py
store_params = {
    'premium': SalesParameters(mean=6.0, std=2.5, ...)  # Increase for higher sales
}

# Temporal smoothing
temporal_model = TemporalSalesModel(smoothing_factor=0.95)  # Lower = more variation

# Brand share targets
brand_controller.adjust_for_target_share(
    sales_data, time_key, 
    target_min=5.0,  # Adjust range
    target_max=12.0
)
```

### Adding New Seasonal Events

```python
# In seasonal_model.py
if 'HALLOWEEN' in product_name:
    if 40 <= week_number <= 44:  # October
        return 3.0  # Triple sales
```

## Performance Optimization

- Samples 5,000 products per time period (configurable)
- Vectorized operations for large calculations
- Hierarchical generation reduces redundant calculations
- Temporal model caches historical values

## Troubleshooting

**Issue**: Hierarchy ratios outside target range
- **Solution**: Adjust `HierarchicalSalesModel` distribution parameters

**Issue**: Excessive temporal variation
- **Solution**: Increase `smoothing_factor` in `TemporalSalesModel`

**Issue**: Brand share not meeting targets
- **Solution**: Check Big Bite product identification, adjust sampling

**Issue**: Memory errors with large datasets
- **Solution**: Reduce `n_products_sample` in `generate_fact_sales()`

## Contributing

When adding new features:
1. Update statistical models in `statistical_models.py`
2. Add validation checks in `validate_constraints.py`
3. Document parameters in this README
4. Run full validation suite before committing

## License

Internal use only - contains proprietary retail modeling algorithms.