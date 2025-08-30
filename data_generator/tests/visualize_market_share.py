#!/usr/bin/env python3
"""
Visualize market share by manufacturer over time
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_data():
    """Load the generated data"""
    print("Loading data...")
    products = pd.read_csv('generated_data/products_dimension.csv')
    fact_sales = pd.read_csv('generated_data/fact_sales.csv')
    time_dim = pd.read_csv('generated_data/time_dimension.csv')
    
    return products, fact_sales, time_dim

def calculate_market_share(products, fact_sales, time_dim):
    """Calculate market share by manufacturer over time"""
    print("Calculating market share...")
    
    # Merge fact sales with products to get manufacturer
    sales_with_mfr = fact_sales.merge(
        products[['Product Key', 'Manufacturer Value', 'Brand Value']], 
        on='Product Key', 
        how='left'
    )
    
    # Group by time and manufacturer
    market_share_data = []
    
    # Limit to available time periods for faster processing
    unique_times = sorted(fact_sales['Time Key'].unique())
    print(f"Processing {len(unique_times)} time periods...")
    
    for time_key in unique_times:
        period_data = sales_with_mfr[sales_with_mfr['Time Key'] == time_key]
        
        # Calculate total sales for the period
        total_sales = period_data['Value Sales'].sum()
        
        if total_sales > 0:
            # Calculate sales by manufacturer
            mfr_sales = period_data.groupby('Manufacturer Value')['Value Sales'].sum()
            
            # Calculate market share
            for mfr, sales in mfr_sales.items():
                market_share_data.append({
                    'Time Key': time_key,
                    'Manufacturer': mfr,
                    'Sales': sales,
                    'Market Share': (sales / total_sales) * 100
                })
    
    market_share_df = pd.DataFrame(market_share_data)
    
    # Add time description for better x-axis
    market_share_df = market_share_df.merge(time_dim, on='Time Key', how='left')
    
    # Convert time description to date
    market_share_df['Date'] = pd.to_datetime(
        market_share_df['Time Description'].str.extract(r'(\d+ \w+, \d+)')[0],
        format='%d %b, %Y'
    )
    
    return market_share_df

def plot_top_manufacturers(market_share_df, top_n=10):
    """Plot market share over time for top manufacturers"""
    print("Creating market share visualization...")
    
    # Get top manufacturers by average market share
    avg_share = market_share_df.groupby('Manufacturer')['Market Share'].mean().sort_values(ascending=False)
    top_manufacturers = avg_share.head(top_n).index.tolist()
    
    # Filter for top manufacturers
    plot_data = market_share_df[market_share_df['Manufacturer'].isin(top_manufacturers)]
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Line chart of market share over time
    for mfr in top_manufacturers:
        mfr_data = plot_data[plot_data['Manufacturer'] == mfr].sort_values('Date')
        ax1.plot(mfr_data['Date'], mfr_data['Market Share'], 
                marker='o', markersize=3, label=mfr, linewidth=2)
    
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Market Share (%)', fontsize=12)
    ax1.set_title('Market Share by Manufacturer Over Time', fontsize=14, fontweight='bold')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, max(plot_data['Market Share'].max() * 1.1, 20))
    
    # Rotate x-axis labels
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 2: Stacked area chart
    pivot_data = plot_data.pivot_table(
        index='Date', 
        columns='Manufacturer', 
        values='Market Share',
        fill_value=0
    )
    
    # Sort columns by average market share
    column_order = pivot_data.mean().sort_values(ascending=False).index
    pivot_data = pivot_data[column_order]
    
    ax2.stackplot(pivot_data.index, 
                  *[pivot_data[col] for col in pivot_data.columns],
                  labels=pivot_data.columns,
                  alpha=0.8)
    
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Market Share (%)', fontsize=12)
    ax2.set_title('Stacked Market Share by Manufacturer', fontsize=14, fontweight='bold')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Rotate x-axis labels
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('../tmp/market_share_manufacturers.png', dpi=300, bbox_inches='tight')
    print("Saved visualization to market_share_manufacturers.png")
    
    return fig

def plot_brand_focus(market_share_df, manufacturer='BIG BITE CHOCOLATES'):
    """Create focused plot for specific manufacturer (e.g., Big Bite)"""
    print(f"Creating focused visualization for {manufacturer}...")
    
    # Filter for specific manufacturer
    mfr_data = market_share_df[market_share_df['Manufacturer'] == manufacturer].sort_values('Date')
    
    if mfr_data.empty:
        print(f"No data found for {manufacturer}")
        return None
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot market share with fill
    ax.plot(mfr_data['Date'], mfr_data['Market Share'], 
            marker='o', markersize=4, linewidth=2.5, color='#2E86AB', label=manufacturer)
    ax.fill_between(mfr_data['Date'], 0, mfr_data['Market Share'], alpha=0.3, color='#2E86AB')
    
    # Add target range (4-10% for Big Bite)
    if 'BIG BITE' in manufacturer:
        ax.axhline(y=4, color='red', linestyle='--', alpha=0.5, label='Target Min (4%)')
        ax.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Target Max (10%)')
        ax.fill_between(mfr_data['Date'], 4, 10, alpha=0.1, color='green', label='Target Range')
    
    # Calculate and display statistics
    avg_share = mfr_data['Market Share'].mean()
    min_share = mfr_data['Market Share'].min()
    max_share = mfr_data['Market Share'].max()
    
    # Add text box with statistics
    textstr = f'Average: {avg_share:.2f}%\nMin: {min_share:.2f}%\nMax: {max_share:.2f}%'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Market Share (%)', fontsize=12)
    ax.set_title(f'{manufacturer} Market Share Over Time', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Set y-axis limits
    if 'BIG BITE' in manufacturer:
        ax.set_ylim(0, 12)
    
    # Rotate x-axis labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save the plot
    filename = f'market_share_{manufacturer.lower().replace(" ", "_")}.png'
    # Update filename to save in tmp directory
    if not filename.startswith('../tmp/'):
        filename = f'../tmp/{filename}'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Saved visualization to {filename}")
    
    return fig

def create_summary_table(market_share_df):
    """Create summary statistics table"""
    print("Creating summary statistics...")
    
    # Calculate summary statistics by manufacturer
    summary = market_share_df.groupby('Manufacturer').agg({
        'Market Share': ['mean', 'std', 'min', 'max'],
        'Sales': 'sum'
    }).round(2)
    
    # Flatten column names
    summary.columns = ['_'.join(col).strip() for col in summary.columns]
    summary = summary.rename(columns={
        'Market Share_mean': 'Avg Share (%)',
        'Market Share_std': 'Std Dev',
        'Market Share_min': 'Min Share (%)',
        'Market Share_max': 'Max Share (%)',
        'Sales_sum': 'Total Sales ($)'
    })
    
    # Sort by average market share
    summary = summary.sort_values('Avg Share (%)', ascending=False)
    
    # Save to CSV
    summary.to_csv('../tmp/market_share_summary.csv')
    print("Saved summary statistics to market_share_summary.csv")
    
    # Display top 15
    print("\nTop 15 Manufacturers by Market Share:")
    print("=" * 80)
    print(summary.head(15).to_string())
    
    return summary

def main():
    """Main execution function"""
    print("=" * 60)
    print("Market Share Analysis")
    print("=" * 60)
    
    # Load data
    products, fact_sales, time_dim = load_data()
    
    # Calculate market share
    market_share_df = calculate_market_share(products, fact_sales, time_dim)
    
    # Create visualizations
    plot_top_manufacturers(market_share_df, top_n=10)
    plot_brand_focus(market_share_df, 'BIG BITE CHOCOLATES')
    
    # Create summary table
    summary = create_summary_table(market_share_df)
    
    # Don't show plots in script mode (they're already saved)
    # plt.show()
    
    print("\n✓ Analysis complete!")
    print("  - market_share_manufacturers.png: Top 10 manufacturers over time")
    print("  - market_share_big_bite_chocolates.png: Big Bite focus chart")
    print("  - market_share_summary.csv: Summary statistics")

if __name__ == "__main__":
    main()