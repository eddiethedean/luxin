"""
Sales Analysis Example - A more realistic use case.

This example demonstrates analyzing sales data with drill-down capability
to explore individual transactions.
"""

import pandas as pd
import numpy as np
from luxin import TrackedDataFrame


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
    print("Sales Analysis by Category")
    print("=" * 60)
    
    agg = df.groupby(['category']).agg({
        'amount': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    })
    
    print(agg)
    
    # In Jupyter, this would display an interactive table
    # agg.show_drill_table()
    
    return agg


def analyze_by_region_and_category(df):
    """Analyze sales by region and category."""
    print("\n\nSales Analysis by Region and Category")
    print("=" * 60)
    
    agg = df.groupby(['region', 'category']).agg({
        'amount': 'sum',
        'quantity': 'sum',
        'transaction_id': 'count'
    })
    
    agg.columns = ['Total Amount', 'Total Quantity', 'Transaction Count']
    
    print(agg.head(10))
    
    # In Jupyter, this would display an interactive table
    # agg.show_drill_table()
    
    return agg


def find_top_customers(df):
    """Find top customers by total purchase amount."""
    print("\n\nTop 10 Customers by Total Purchase Amount")
    print("=" * 60)
    
    agg = df.groupby(['customer_id']).agg({
        'amount': 'sum',
        'transaction_id': 'count'
    })
    
    agg.columns = ['Total Amount', 'Number of Transactions']
    agg = agg.sort_values('Total Amount', ascending=False).head(10)
    
    print(agg)
    
    # In Jupyter, clicking on a customer would show all their transactions
    # agg.show_drill_table()
    
    return agg


if __name__ == '__main__':
    # Generate sample data
    df = generate_sales_data(100)
    
    print("Sample Sales Data (first 10 rows):")
    print(df.head(10))
    print(f"\nTotal records: {len(df)}")
    
    # Run analyses
    analyze_by_category(df)
    analyze_by_region_and_category(df)
    find_top_customers(df)
    
    print("\n\nNote: Run this in Jupyter notebook and uncomment .show_drill_table()")
    print("to see the interactive drill-down tables!")

