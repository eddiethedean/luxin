"""
Basic usage example for Luxin.

This example demonstrates the new Inspector API for Streamlit-first
interactive data exploration with drill-down capabilities.
"""

import pandas as pd
import streamlit as st
from luxin import Inspector, TrackedDataFrame


def example_inspector():
    """Example using Inspector API (recommended approach)."""
    st.header("Example 1: Using Inspector API")
    
    # Create sample data
    data = {
        'category': ['Electronics', 'Electronics', 'Clothing', 'Clothing', 'Food', 'Food'],
        'product': ['Laptop', 'Mouse', 'Shirt', 'Pants', 'Apple', 'Banana'],
        'sales': [1000, 50, 30, 45, 2, 1],
        'profit': [200, 10, 10, 15, 0.5, 0.3]
    }
    
    # Create TrackedDataFrame
    df = TrackedDataFrame(data)
    
    # Aggregate - tracking happens automatically
    agg = df.groupby(['category']).agg({
        'sales': 'sum',
        'profit': 'sum'
    })
    
    # Use Inspector to render interactive view
    inspector = Inspector(agg)
    inspector.render()


def example_regular_dataframe():
    """Example using Inspector with regular pandas DataFrame."""
    st.header("Example 2: Using Inspector with Regular DataFrame")
    
    # Your existing pandas workflow
    df = pd.DataFrame({
        'region': ['North', 'North', 'South', 'South', 'East', 'West'],
        'sales': [100, 150, 200, 250, 175, 125],
        'expenses': [50, 60, 80, 90, 70, 55]
    })
    
    # Convert to TrackedDataFrame for aggregation tracking
    tracked_df = TrackedDataFrame(df)
    
    # Your existing aggregation
    agg_df = tracked_df.groupby('region').agg({
        'sales': 'sum',
        'expenses': 'sum'
    })
    
    # Use Inspector to render
    inspector = Inspector(agg_df)
    inspector.render()


def example_multi_column_groupby():
    """Example with multiple groupby columns."""
    st.header("Example 3: Multi-Column GroupBy")
    
    data = {
        'region': ['North', 'North', 'North', 'South', 'South', 'South'],
        'product': ['A', 'A', 'B', 'A', 'B', 'B'],
        'sales': [100, 150, 200, 120, 180, 220],
        'units': [10, 15, 8, 12, 9, 11]
    }
    
    df = TrackedDataFrame(data)
    
    # Group by multiple columns
    agg = df.groupby(['region', 'product']).agg({
        'sales': ['sum', 'mean'],
        'units': 'sum'
    })
    
    # Use Inspector to render
    inspector = Inspector(agg)
    inspector.render()


if __name__ == '__main__':
    st.set_page_config(page_title="Luxin Examples", page_icon="📊", layout="wide")
    st.title("📊 Luxin Interactive Data Exploration Examples")
    
    example_inspector()
    st.divider()
    example_regular_dataframe()
    st.divider()
    example_multi_column_groupby()

