#!/usr/bin/env python3
"""
Statistical models for hierarchical sales generation with temporal consistency
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SalesParameters:
    """Parameters for sales distribution by store type"""
    mean: float
    std: float
    min_val: float
    max_val: float


class HierarchicalSalesModel:
    """Generates sales with proper hierarchical aggregation"""
    
    def __init__(self, geography_df: pd.DataFrame, products_df: pd.DataFrame, time_df: pd.DataFrame):
        self.geography = geography_df
        self.products = products_df
        self.time = time_df
        
        # Store type parameters for log-normal distribution
        self.store_params = {
            'IRI All Outlets': SalesParameters(mean=6.0, std=2.5, min_val=10, max_val=100000),
            'premium': SalesParameters(mean=5.5, std=2.0, min_val=5, max_val=50000),
            'major': SalesParameters(mean=5.0, std=2.2, min_val=2, max_val=40000),
            'discount': SalesParameters(mean=4.5, std=2.3, min_val=1, max_val=30000),
            'convenience': SalesParameters(mean=3.5, std=1.8, min_val=0.5, max_val=10000),
            'online': SalesParameters(mean=4.0, std=2.0, min_val=1, max_val=20000),
        }
        
        # Build hierarchy structure
        self.hierarchy = self._build_hierarchy()
        
    def _build_hierarchy(self) -> Dict:
        """Build parent-child relationships from geography"""
        hierarchy = {}
        
        # Group by parent
        for _, row in self.geography.iterrows():
            if pd.isna(row['parent_key']):
                hierarchy[row['geography_key']] = {
                    'name': row['geography_description'],
                    'level': 0,
                    'children': [],
                    'parent': None
                }
            else:
                if row['parent_key'] not in hierarchy:
                    hierarchy[row['parent_key']] = {'children': []}
                hierarchy[row['parent_key']]['children'].append(row['geography_key'])
                
                hierarchy[row['geography_key']] = {
                    'name': row['geography_description'],
                    'level': row['hierarchy_level'],
                    'parent': row['parent_key'],
                    'children': []
                }
        
        return hierarchy
    
    def _get_store_type(self, store_name: str) -> str:
        """Classify store into type for parameter selection"""
        store_lower = store_name.lower()
        
        if store_name == 'IRI All Outlets':
            return 'IRI All Outlets'
        elif 'waitrose' in store_lower:
            return 'premium'
        elif 'aldi' in store_lower or 'lidl' in store_lower or 'poundland' in store_lower:
            return 'discount'
        elif 'online' in store_lower:
            return 'online'
        elif any(x in store_lower for x in ['express', 'local', 'metro', 'convenience']):
            return 'convenience'
        else:
            return 'major'
    
    def generate_hierarchical_sales(self, product_key: int, time_key: int, 
                                   base_multiplier: float = 1.0) -> Dict[int, float]:
        """Generate sales respecting hierarchy constraints"""
        sales = {}
        
        # Find IRI All Outlets key
        iri_key = self.geography[self.geography['geography_description'] == 'IRI All Outlets']['geography_key'].iloc[0]
        
        # Generate top-level sales
        params = self.store_params['IRI All Outlets']
        iri_sales = np.random.lognormal(params.mean, params.std) * base_multiplier
        iri_sales = np.clip(iri_sales, params.min_val, params.max_val)
        sales[iri_key] = iri_sales
        
        # Calculate target for Level 1 (40% of IRI total)
        level1_target = iri_sales / 2.5
        
        # Get Level 1 stores
        level1_stores = self.geography[self.geography['hierarchy_level'] == 1]
        
        # Distribute to Level 1 based on store type weights
        weights = []
        for _, store in level1_stores.iterrows():
            store_type = self._get_store_type(store['geography_description'])
            if store_type == 'premium':
                weights.append(1.5)
            elif store_type == 'discount':
                weights.append(0.7)
            else:
                weights.append(1.0)
        
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Allocate sales to Level 1
        for i, (_, store) in enumerate(level1_stores.iterrows()):
            if store['geography_key'] == iri_key:
                continue
                
            store_sales = level1_target * weights[i] * np.random.uniform(0.9, 1.1)
            store_type = self._get_store_type(store['geography_description'])
            params = self.store_params[store_type]
            
            # Add some noise
            store_sales *= np.random.uniform(0.8, 1.2)
            store_sales = np.clip(store_sales, params.min_val, params.max_val)
            sales[store['geography_key']] = store_sales
            
            # Distribute to Level 2 children (30-70% of parent)
            children = self.hierarchy.get(store['geography_key'], {}).get('children', [])
            if children:
                child_pct = np.random.uniform(0.3, 0.7)
                remaining = store_sales * child_pct
                
                for child_key in children:
                    child_store = self.geography[self.geography['geography_key'] == child_key]
                    if not child_store.empty:
                        child_name = child_store.iloc[0]['geography_description']
                        
                        # Online typically gets 10-30% of parent
                        if 'Online' in child_name:
                            child_sales = store_sales * np.random.uniform(0.1, 0.3)
                        else:
                            child_sales = remaining * np.random.uniform(0.2, 0.5)
                        
                        sales[child_key] = child_sales
        
        return sales


class BrandStoryGenerator:
    """Creates realistic trending patterns and stories for brands"""
    
    def __init__(self):
        # Define brand stories with trends and events
        self.brand_stories = {
            'BIG BITE CHOCOLATES': {
                'overall_trend': 'growth',  # Growing brand
                'annual_growth': 0.15,  # 15% year-over-year growth
                'declining_products': ['BIG BITE ORIGINAL'],  # Original losing to newer variants
                'star_products': ['BIG BITE DELUXE', 'BIG BITE VELVET'],  # Premium variants growing
                'events': [
                    {'week': 2230, 'type': 'campaign', 'impact': 1.3},  # Marketing campaign
                    {'week': 2280, 'type': 'innovation', 'impact': 1.2},  # New product launch
                    {'week': 2340, 'type': 'viral', 'impact': 1.5},  # Social media viral moment
                ]
            },
            'MONDELEZ': {
                'overall_trend': 'stable',
                'annual_growth': 0.02,  # Mature brand, slow growth
                'declining_products': [],
                'star_products': [],
                'events': [
                    {'week': 2250, 'type': 'recall', 'impact': 0.7},  # Product recall
                    {'week': 2320, 'type': 'relaunch', 'impact': 1.1},
                ]
            },
            'MARS': {
                'overall_trend': 'decline',
                'annual_growth': -0.05,  # Losing market share
                'events': [
                    {'week': 2260, 'type': 'competitor', 'impact': 0.85},  # Competitor pressure
                ]
            },
            'PRIVATE LABEL': {
                'overall_trend': 'growth',
                'annual_growth': 0.08,  # Growing due to cost of living
                'events': [
                    {'week': 2300, 'type': 'expansion', 'impact': 1.15},  # Range expansion
                ]
            },
            'LINDT': {
                'overall_trend': 'seasonal_stable',
                'annual_growth': 0.03,
                'events': [
                    {'week': 2245, 'type': 'premium', 'impact': 1.1},  # Premium positioning
                ]
            },
            'FERRERO': {
                'overall_trend': 'growth',
                'annual_growth': 0.06,
                'events': [
                    {'week': 2290, 'type': 'innovation', 'impact': 1.2},
                ]
            }
        }
        
        # Default story for brands not explicitly defined
        self.default_story = {
            'overall_trend': 'stable',
            'annual_growth': 0.0,
            'events': []
        }
    
    def get_trend_multiplier(self, brand: str, time_key: int, base_time: int = 2201) -> float:
        """Calculate trend multiplier based on brand story"""
        story = self.brand_stories.get(brand, self.default_story)
        
        # Calculate weeks since start
        weeks_elapsed = time_key - base_time
        years_elapsed = weeks_elapsed / 52
        
        # Base trend multiplier
        if story['overall_trend'] == 'growth':
            trend_mult = 1.0 + (story['annual_growth'] * years_elapsed)
        elif story['overall_trend'] == 'decline':
            trend_mult = 1.0 + (story['annual_growth'] * years_elapsed)  # negative growth
        else:
            trend_mult = 1.0 + (story['annual_growth'] * years_elapsed)
        
        # Add some realistic noise to the trend
        trend_mult *= np.random.normal(1.0, 0.02)  # ±2% random variation
        
        # Apply event impacts
        for event in story.get('events', []):
            if abs(time_key - event['week']) <= 4:  # Event affects ±4 weeks
                distance = abs(time_key - event['week'])
                # Gaussian decay from event center
                event_impact = 1 + (event['impact'] - 1) * np.exp(-0.5 * (distance / 2) ** 2)
                trend_mult *= event_impact
        
        return max(0.1, min(3.0, trend_mult))  # Cap between 0.1x and 3x
    
    def get_product_lifecycle_multiplier(self, brand: str, product_name: str, time_key: int) -> float:
        """Apply product-specific lifecycle patterns"""
        story = self.brand_stories.get(brand, {})
        
        # Check if product is declining
        if product_name in story.get('declining_products', []):
            weeks_elapsed = time_key - 2201
            decline_rate = -0.002 * weeks_elapsed  # -0.2% per week
            return max(0.3, 1.0 + decline_rate)  # Floor at 30% of original
        
        # Check if product is a star
        if product_name in story.get('star_products', []):
            weeks_elapsed = time_key - 2201
            growth_rate = 0.003 * weeks_elapsed  # +0.3% per week
            return min(2.5, 1.0 + growth_rate)  # Cap at 250% of original
        
        return 1.0


class TemporalSalesModel:
    """Manages temporal consistency in sales data with smooth trends"""
    
    def __init__(self, smoothing_factor: float = 0.95):
        self.smoothing_factor = smoothing_factor
        self.sales_history = {}  # Track historical sales
        self.brand_story_gen = BrandStoryGenerator()
        
    def apply_temporal_smoothing(self, geo_key: int, product_key: int, time_key: int, 
                                base_sales: float, brand: str = None, 
                                product_name: str = None) -> float:
        """Apply AR(1) model with brand trends for smooth temporal consistency"""
        
        # Create unique key for tracking
        tracking_key = (geo_key, product_key)
        
        # Get brand trend multiplier if brand provided
        trend_mult = 1.0
        if brand:
            trend_mult = self.brand_story_gen.get_trend_multiplier(brand, time_key)
            if product_name:
                # Apply product-specific lifecycle
                lifecycle_mult = self.brand_story_gen.get_product_lifecycle_multiplier(
                    brand, product_name, time_key
                )
                trend_mult *= lifecycle_mult
        
        # Apply trend to base sales
        base_sales *= trend_mult
        
        # Get previous period sales if exists
        prev_time_key = time_key - 1
        prev_key = (*tracking_key, prev_time_key)
        
        if prev_key in self.sales_history:
            prev_sales = self.sales_history[prev_key]
            
            # Strong smoothing for realistic trends
            # AR(1) model with high persistence
            beta = np.random.uniform(0.97, 1.03)  # Much tighter range for smoother trends
            
            # Small noise relative to sales level
            epsilon = np.random.normal(0, prev_sales * 0.005)  # Very small noise (0.5%)
            
            smoothed_sales = beta * prev_sales + epsilon
            
            # Heavy weighting to previous period for smooth trends
            final_sales = 0.85 * smoothed_sales + 0.15 * base_sales
        else:
            # No history, use base sales with very small variation
            final_sales = base_sales * np.random.uniform(0.98, 1.02)
        
        # Store for next period
        current_key = (*tracking_key, time_key)
        self.sales_history[current_key] = final_sales
        
        return max(0, final_sales)  # Ensure non-negative


class BrandShareController:
    """Ensures brand share targets are met"""
    
    def __init__(self, products_df: pd.DataFrame):
        self.products = products_df
        self.big_bite_products = self._identify_big_bite_products()
        
    def _identify_big_bite_products(self) -> List[int]:
        """Find all Big Bite Chocolate products"""
        big_bite = self.products[
            self.products['brand_value'].str.contains('BIG BITE', case=False, na=False)
        ]
        return big_bite['product_key'].tolist()
    
    def calculate_market_share(self, sales_data: pd.DataFrame, time_key: int) -> float:
        """Calculate Big Bite market share for a time period"""
        if sales_data.empty:
            return 0.0
            
        period_data = sales_data[sales_data['time_key'] == time_key]
        if period_data.empty:
            return 0.0
        
        total_sales = period_data['value_sales'].sum()
        big_bite_sales = period_data[
            period_data['product_key'].isin(self.big_bite_products)
        ]['value_sales'].sum()
        
        return (big_bite_sales / total_sales * 100) if total_sales > 0 else 0.0
    
    def adjust_for_target_share(self, sales_data: pd.DataFrame, time_key: int,
                               target_min: float = 4.0, target_max: float = 10.0) -> pd.DataFrame:
        """Adjust sales to meet Big Bite share targets with growth trend"""
        # Adjust target range based on time (Big Bite is growing)
        weeks_elapsed = time_key - 2201
        years_elapsed = weeks_elapsed / 52
        
        # Big Bite grows from 4-6% to 7-10% over 4 years
        adjusted_min = min(7.0, 4.0 + (years_elapsed * 0.75))  # Grows to 7%
        adjusted_max = min(10.0, 6.0 + (years_elapsed * 1.0))  # Grows to 10%
        
        current_share = self.calculate_market_share(sales_data, time_key)
        
        if current_share < adjusted_min or current_share > adjusted_max:
            # Calculate adjustment factor
            target_share = np.random.uniform(adjusted_min, adjusted_max)
            
            period_mask = sales_data['time_key'] == time_key
            big_bite_mask = sales_data['product_key'].isin(self.big_bite_products)
            
            total_sales = sales_data.loc[period_mask, 'value_sales'].sum()
            current_big_bite = sales_data.loc[period_mask & big_bite_mask, 'value_sales'].sum()
            
            if current_big_bite > 0:
                # Calculate required Big Bite sales
                required_big_bite = total_sales * (target_share / 100)
                adjustment_factor = required_big_bite / current_big_bite
                
                # Apply adjustment to Big Bite products
                sales_data.loc[period_mask & big_bite_mask, 'value_sales'] *= adjustment_factor
                sales_data.loc[period_mask & big_bite_mask, 'unit_sales'] *= adjustment_factor
                sales_data.loc[period_mask & big_bite_mask, 'volume_sales'] *= adjustment_factor
        
        return sales_data


class SeasonalModel:
    """Handles seasonal patterns with smooth transitions"""
    
    def __init__(self, products_df: pd.DataFrame):
        self.products = products_df
        self._identify_seasonal_products()
    
    def _identify_seasonal_products(self):
        """Categorize products by seasonality"""
        self.seasonal = {
            'christmas': self.products[
                (self.products['subsegment_value'].str.contains('ADVENT|CHRISTMAS|SELECTION', case=False, na=False)) |
                (self.products['segment_value'].str.contains('SEASONAL|GIFTING', case=False, na=False))
            ]['product_key'].tolist(),
            
            'easter': self.products[
                self.products['subsegment_value'].str.contains('EASTER|EGG', case=False, na=False)
            ]['product_key'].tolist(),
            
            'valentine': self.products[
                self.products['subsegment_value'].str.contains('VALENTINE|HEART', case=False, na=False)
            ]['product_key'].tolist()
        }
    
    def get_seasonal_multiplier(self, product_key: int, week_number: int) -> float:
        """Calculate smooth seasonal multiplier"""
        
        # Christmas products (weeks 44-52 with peak at 51)
        if product_key in self.seasonal['christmas']:
            if 44 <= week_number <= 52:
                # Smooth bell curve centered on week 51
                peak_week = 51
                distance = abs(week_number - peak_week)
                multiplier = 5.0 * np.exp(-0.1 * distance)
                return max(2.0, multiplier)
            else:
                return 0.1  # Minimal sales outside season
        
        # Easter products (weeks 10-16 with peak at 14)
        elif product_key in self.seasonal['easter']:
            if 10 <= week_number <= 16:
                peak_week = 14
                distance = abs(week_number - peak_week)
                multiplier = 4.0 * np.exp(-0.15 * distance)
                return max(2.0, multiplier)
            else:
                return 0.05
        
        # Valentine products (weeks 5-7 with peak at 6)
        elif product_key in self.seasonal['valentine']:
            if 5 <= week_number <= 7:
                peak_week = 6
                distance = abs(week_number - peak_week)
                multiplier = 2.5 * np.exp(-0.5 * distance)
                return max(1.5, multiplier)
            else:
                return 0.1
        
        # Regular products - mild seasonal variation
        else:
            if 48 <= week_number <= 52:
                return np.random.uniform(1.1, 1.3)  # Christmas boost
            elif 10 <= week_number <= 16:
                return np.random.uniform(1.2, 1.4)  # Easter boost
            elif 26 <= week_number <= 35:
                return np.random.uniform(0.7, 0.8)  # Summer lull
            else:
                return 1.0


class PriceElasticityModel:
    """Models price-volume relationships"""
    
    def __init__(self, elasticity_range: Tuple[float, float] = (-1.2, -0.8)):
        self.elasticity_range = elasticity_range
    
    def calculate_volume_from_price(self, base_volume: float, price_change_pct: float, 
                                   product_type: str = 'standard') -> float:
        """Calculate volume impact from price changes"""
        
        # Different elasticities by product type
        if product_type == 'premium':
            elasticity = np.random.uniform(-0.6, -0.4)  # Less elastic
        elif product_type == 'value':
            elasticity = np.random.uniform(-1.5, -1.2)  # More elastic
        else:
            elasticity = np.random.uniform(*self.elasticity_range)
        
        # Volume change = elasticity * price change
        volume_change_pct = elasticity * price_change_pct
        new_volume = base_volume * (1 + volume_change_pct / 100)
        
        return max(0, new_volume)