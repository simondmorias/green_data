#!/usr/bin/env python3
"""
Visualize market trends and brand stories over time
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def load_and_process_data():
    """Load and process the generated data"""
    print("Loading data...")
    products = pd.read_csv('generated_data/products_dimension.csv')
    fact_sales = pd.read_csv('generated_data/fact_sales.csv')
    time_dim = pd.read_csv('generated_data/time_dimension.csv')
    
    # Merge to get manufacturer info
    sales_with_info = fact_sales.merge(
        products[['Product Key', 'Manufacturer Value', 'Brand Value']], 
        on='Product Key'
    )
    
    # Add time info
    sales_with_info = sales_with_info.merge(time_dim, on='Time Key')
    
    # Parse dates
    sales_with_info['Date'] = pd.to_datetime(
        sales_with_info['Time Description'].str.extract(r'(\d+ \w+, \d+)')[0],
        format='%d %b, %Y'
    )
    
    return sales_with_info, products

def plot_manufacturer_trends(sales_data):
    """Plot smooth trends for key manufacturers"""
    print("Creating manufacturer trend visualization...")
    
    # Aggregate by manufacturer and time
    mfr_trends = sales_data.groupby(['Date', 'Manufacturer Value'])['Value Sales'].sum().reset_index()
    
    # Calculate market share
    total_by_date = mfr_trends.groupby('Date')['Value Sales'].sum()
    mfr_trends = mfr_trends.merge(
        total_by_date.rename('Total Sales'), 
        left_on='Date', 
        right_index=True
    )
    mfr_trends['Market Share'] = (mfr_trends['Value Sales'] / mfr_trends['Total Sales']) * 100
    
    # Focus on key manufacturers with stories
    key_mfrs = ['BIG BITE CHOCOLATES', 'MONDELEZ', 'MARS', 'PRIVATE LABEL', 'LINDT', 'FERRERO']
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    
    for idx, mfr in enumerate(key_mfrs):
        ax = axes[idx]
        mfr_data = mfr_trends[mfr_trends['Manufacturer Value'] == mfr].sort_values('Date')
        
        if not mfr_data.empty:
            # Plot trend line
            ax.plot(mfr_data['Date'], mfr_data['Market Share'], 
                   linewidth=2.5, marker='o', markersize=2)
            
            # Add trend line
            z = np.polyfit(range(len(mfr_data)), mfr_data['Market Share'], 1)
            p = np.poly1d(z)
            ax.plot(mfr_data['Date'], p(range(len(mfr_data))), 
                   "--", alpha=0.5, color='red', label='Trend')
            
            # Annotations for brand stories
            if mfr == 'BIG BITE CHOCOLATES':
                ax.set_title(f'{mfr}\n(Growing Brand, +15% YoY)', fontweight='bold')
                ax.axhline(y=4, color='green', linestyle=':', alpha=0.3, label='Initial target')
                ax.axhline(y=10, color='green', linestyle=':', alpha=0.3, label='Growth target')
            elif mfr == 'MARS':
                ax.set_title(f'{mfr}\n(Declining, -5% YoY)', fontweight='bold')
            elif mfr == 'PRIVATE LABEL':
                ax.set_title(f'{mfr}\n(Growing, +8% YoY)', fontweight='bold')
            elif mfr == 'MONDELEZ':
                ax.set_title(f'{mfr}\n(Stable, +2% YoY)', fontweight='bold')
            else:
                ax.set_title(mfr, fontweight='bold')
            
            ax.set_xlabel('Date')
            ax.set_ylabel('Market Share (%)')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best', fontsize=8)
            
            # Rotate x labels
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.suptitle('Manufacturer Market Share Trends (2022-2025)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig('../tmp/manufacturer_trends.png', dpi=300, bbox_inches='tight')
    print("Saved to manufacturer_trends.png")
    
    return fig

def plot_big_bite_story(sales_data, products):
    """Detailed Big Bite brand story visualization"""
    print("Creating Big Bite brand story visualization...")
    
    # Filter for Big Bite
    big_bite_sales = sales_data[
        sales_data['Brand Value'].str.contains('BIG BITE', case=False, na=False)
    ]
    
    if big_bite_sales.empty:
        print("No Big Bite data found")
        return None
    
    # Aggregate by product variant
    variant_trends = big_bite_sales.groupby(['Date', 'Brand Value'])['Value Sales'].sum().reset_index()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Overall Big Bite trend
    total_bb = variant_trends.groupby('Date')['Value Sales'].sum().reset_index()
    ax1.plot(total_bb['Date'], total_bb['Value Sales'] / 1000, 
            linewidth=3, color='#2E86AB', marker='o', markersize=4)
    ax1.fill_between(total_bb['Date'], 0, total_bb['Value Sales'] / 1000, 
                     alpha=0.3, color='#2E86AB')
    
    # Mark key events
    events = [
        ('2022-06', 'Launch'),
        ('2022-11', 'Marketing\nCampaign'),
        ('2023-05', 'Innovation\nLaunch'),
        ('2024-03', 'Viral\nMoment')
    ]
    
    for event_date, event_name in events:
        event_dt = pd.to_datetime(event_date)
        if event_dt <= total_bb['Date'].max():
            ax1.axvline(x=event_dt, color='red', linestyle='--', alpha=0.5)
            ax1.text(event_dt, ax1.get_ylim()[1] * 0.9, event_name, 
                    rotation=0, ha='center', fontsize=9)
    
    ax1.set_title('Big Bite Chocolates: Growth Story', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Sales ($000s)')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Product variant performance
    for variant in variant_trends['Brand Value'].unique():
        variant_data = variant_trends[variant_trends['Brand Value'] == variant].sort_values('Date')
        
        label = variant
        if 'ORIGINAL' in variant:
            label += ' (Declining)'
            linestyle = '--'
        elif 'DELUXE' in variant or 'VELVET' in variant:
            label += ' (Star)'
            linestyle = '-'
        else:
            linestyle = '-.'
        
        ax2.plot(variant_data['Date'], variant_data['Value Sales'] / 1000,
                label=label, linewidth=2, linestyle=linestyle, marker='o', markersize=2)
    
    ax2.set_title('Product Variant Performance', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Sales ($000s)')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Rotate x labels
    for ax in [ax1, ax2]:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('../tmp/big_bite_story.png', dpi=300, bbox_inches='tight')
    print("Saved to big_bite_story.png")
    
    return fig

def analyze_trend_quality(sales_data):
    """Analyze the quality of trends (smoothness)"""
    print("\nAnalyzing trend quality...")
    
    # Calculate week-over-week changes
    mfr_weekly = sales_data.groupby(['Time Key', 'Manufacturer Value'])['Value Sales'].sum().reset_index()
    
    results = []
    for mfr in ['BIG BITE CHOCOLATES', 'MONDELEZ', 'MARS', 'PRIVATE LABEL']:
        mfr_data = mfr_weekly[mfr_weekly['Manufacturer Value'] == mfr].sort_values('Time Key')
        if len(mfr_data) > 1:
            mfr_data['WoW_Change'] = mfr_data['Value Sales'].pct_change()
            
            # Calculate smoothness metrics
            avg_change = mfr_data['WoW_Change'].mean()
            volatility = mfr_data['WoW_Change'].std()
            
            results.append({
                'Manufacturer': mfr,
                'Avg Weekly Change': f"{avg_change*100:.2f}%",
                'Volatility (StdDev)': f"{volatility*100:.2f}%",
                'Smoothness': 'Good' if volatility < 0.05 else 'Moderate' if volatility < 0.10 else 'Poor'
            })
    
    results_df = pd.DataFrame(results)
    print("\nTrend Quality Analysis:")
    print("=" * 60)
    print(results_df.to_string(index=False))
    
    return results_df

def main():
    """Main execution"""
    print("=" * 60)
    print("Market Trend Analysis with Brand Stories")
    print("=" * 60)
    
    # Load data
    sales_data, products = load_and_process_data()
    
    # Create visualizations
    plot_manufacturer_trends(sales_data)
    plot_big_bite_story(sales_data, products)
    
    # Analyze quality
    quality_df = analyze_trend_quality(sales_data)
    quality_df.to_csv('../tmp/trend_quality_analysis.csv', index=False)
    
    print("\n✓ Analysis complete!")
    print("Generated files:")
    print("  - manufacturer_trends.png: Trends for 6 key manufacturers")
    print("  - big_bite_story.png: Detailed Big Bite growth story")
    print("  - trend_quality_analysis.csv: Smoothness metrics")

if __name__ == "__main__":
    main()