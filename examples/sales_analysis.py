"""
Sales Analysis Example - A more realistic use case.

This example demonstrates analyzing sales data with drill-down capability
to explore individual transactions using the Inspector API.
"""

import pandas as pd
import numpy as np
import streamlit as st
from luxin import Inspector, TrackedDataFrame


def generate_sales_data(n_transactions=100):
    """Generate sample sales data."""
    np.random.seed(42)
    
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home & Garden']
    regions = ['North', 'South', 'East', 'West']
    
    data = {
        'transaction_id': range(1, n_transactions + 1),
        'category': np.random.choice(categories, n_transactions),
        'region': np.random.choice(regions, n_transactions),
        'amount': np.random.uniform(10, 500, n_transactions).round(2),
        'quantity': np.random.randint(1, 10, n_transactions),
        'customer_id': np.random.randint(1000, 2000, n_transactions)
    }
    
    return TrackedDataFrame(data)


def analyze_by_category(df):
    """Analyze sales by category."""
    st.header("Sales Analysis by Category")
    
    agg = df.groupby(['category']).agg({
        'amount': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    })
    
    # Use Inspector to render interactive view
    inspector = Inspector(agg)
    inspector.render()
    
    return agg


def analyze_by_region_and_category(df):
    """Analyze sales by region and category."""
    st.header("Sales Analysis by Region and Category")
    
    agg = df.groupby(['region', 'category']).agg({
        'amount': 'sum',
        'quantity': 'sum',
        'transaction_id': 'count'
    })
    
    agg.columns = ['Total Amount', 'Total Quantity', 'Transaction Count']
    
    # Use Inspector to render interactive view
    inspector = Inspector(agg)
    inspector.render()
    
    return agg


def find_top_customers(df):
    """Find top customers by total purchase amount."""
    st.header("Top 10 Customers by Total Purchase Amount")
    
    agg = df.groupby(['customer_id']).agg({
        'amount': 'sum',
        'transaction_id': 'count'
    })
    
    agg.columns = ['Total Amount', 'Number of Transactions']
    agg = agg.sort_values('Total Amount', ascending=False).head(10)
    
    # Use Inspector to render interactive view
    inspector = Inspector(agg)
    inspector.render()
    
    return agg


if __name__ == '__main__':
    st.set_page_config(page_title="Sales Analysis", page_icon="💰", layout="wide")
    st.title("💰 Sales Analysis with Drill-Down Exploration")
    
    # Generate sample data
    df = generate_sales_data(100)
    
    st.sidebar.header("Dataset Info")
    st.sidebar.metric("Total Records", len(df))
    st.sidebar.metric("Categories", df['category'].nunique())
    st.sidebar.metric("Regions", df['region'].nunique())
    
    # Run analyses
    analyze_by_category(df)
    st.divider()
    analyze_by_region_and_category(df)
    st.divider()
    find_top_customers(df)

