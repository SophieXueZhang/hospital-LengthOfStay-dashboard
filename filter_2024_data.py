#!/usr/bin/env python3
"""
Filter LengthOfStay.csv to keep only 2024 data, remove 2025 records
"""

import pandas as pd
from datetime import datetime

def filter_2024_data():
    """Remove 2025 records, keep only 2024 data"""
    
    file_path = '/Users/pc/Documents/cursor/ml_course/project/data/LengthOfStay.csv'
    print("Loading CSV file...")
    df = pd.read_csv(file_path)
    
    print(f"Original dataset shape: {df.shape}")
    
    # Convert vdate to datetime to filter by year
    df['vdate_dt'] = pd.to_datetime(df['vdate'], format='%m/%d/%Y')
    
    # Check year distribution before filtering
    year_counts = df['vdate_dt'].dt.year.value_counts().sort_index()
    print(f"Year distribution before filtering:")
    for year, count in year_counts.items():
        print(f"  {year}: {count} records")
    
    # Filter to keep only 2024 data
    df_2024 = df[df['vdate_dt'].dt.year == 2024].copy()
    
    # Drop the temporary datetime column
    df_2024 = df_2024.drop('vdate_dt', axis=1)
    
    print(f"Filtered dataset shape: {df_2024.shape}")
    print(f"Removed {len(df) - len(df_2024)} records from 2025")
    
    # Verify all remaining records are 2024
    df_2024['vdate_check'] = pd.to_datetime(df_2024['vdate'], format='%m/%d/%Y')
    remaining_years = df_2024['vdate_check'].dt.year.value_counts().sort_index()
    print(f"Year distribution after filtering:")
    for year, count in remaining_years.items():
        print(f"  {year}: {count} records")
    
    # Drop the check column
    df_2024 = df_2024.drop('vdate_check', axis=1)
    
    # Save the filtered data
    print(f"\nSaving filtered CSV file...")
    df_2024.to_csv(file_path, index=False)
    print("Done!")
    
    # Show sample of remaining data
    print(f"\nSample of remaining data:")
    print(df_2024[['First_Name', 'Last_Name', 'vdate', 'discharged']].head())

if __name__ == "__main__":
    filter_2024_data()