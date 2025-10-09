"""
Basic usage example for Luxin.

This example demonstrates both the automatic tracking (TrackedDataFrame)
and manual API (create_drill_table) approaches.
"""

import pandas as pd
from luxin import TrackedDataFrame, create_drill_table


def example_tracked_dataframe():
    """Example using TrackedDataFrame for automatic tracking."""
    print("Example 1: Using TrackedDataFrame (Automatic Tracking)")
    print("=" * 60)
    
    # Create sample data
    data = {
        'category': ['Electronics', 'Electronics', 'Clothing', 'Clothing', 'Food', 'Food'],
        'product': ['Laptop', 'Mouse', 'Shirt', 'Pants', 'Apple', 'Banana'],
        'sales': [1000, 50, 30, 45, 2, 1],
        'profit': [200, 10, 10, 15, 0.5, 0.3]
    }
    
    # Create TrackedDataFrame
    df = TrackedDataFrame(data)
    print("\nOriginal Data:")
    print(df)
    
    # Aggregate - tracking happens automatically
    agg = df.groupby(['category']).agg({
        'sales': 'sum',
        'profit': 'sum'
    })
    
    print("\nAggregated Data:")
    print(agg)
    
    # Display with drill-down (uncomment in Jupyter)
    # agg.show_drill_table()
    
    print("\nSource mapping created:")
    for key, indices in agg._source_mapping.items():
        print(f"  {key}: {indices}")


def example_manual_api():
    """Example using manual API for existing DataFrames."""
    print("\n\nExample 2: Using Manual API")
    print("=" * 60)
    
    # Your existing pandas workflow
    df = pd.DataFrame({
        'region': ['North', 'North', 'South', 'South', 'East', 'West'],
        'sales': [100, 150, 200, 250, 175, 125],
        'expenses': [50, 60, 80, 90, 70, 55]
    })
    
    print("\nOriginal Data:")
    print(df)
    
    # Your existing aggregation
    agg_df = df.groupby('region').agg({
        'sales': 'sum',
        'expenses': 'sum'
    })
    
    print("\nAggregated Data:")
    print(agg_df)
    
    # Create drill-down table (uncomment in Jupyter)
    # create_drill_table(agg_df, df, groupby_cols=['region'])
    
    print("\nYou can now use create_drill_table() in Jupyter to explore!")


def example_multi_column_groupby():
    """Example with multiple groupby columns."""
    print("\n\nExample 3: Multi-Column GroupBy")
    print("=" * 60)
    
    data = {
        'region': ['North', 'North', 'North', 'South', 'South', 'South'],
        'product': ['A', 'A', 'B', 'A', 'B', 'B'],
        'sales': [100, 150, 200, 120, 180, 220],
        'units': [10, 15, 8, 12, 9, 11]
    }
    
    df = TrackedDataFrame(data)
    print("\nOriginal Data:")
    print(df)
    
    # Group by multiple columns
    agg = df.groupby(['region', 'product']).agg({
        'sales': ['sum', 'mean'],
        'units': 'sum'
    })
    
    print("\nAggregated Data:")
    print(agg)
    
    # Display (uncomment in Jupyter)
    # agg.show_drill_table()


if __name__ == '__main__':
    example_tracked_dataframe()
    example_manual_api()
    example_multi_column_groupby()
    
    print("\n\nTo see the interactive drill-down tables, run these examples in a Jupyter notebook!")

