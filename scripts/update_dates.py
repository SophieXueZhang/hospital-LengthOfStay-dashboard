#!/usr/bin/env python3
"""
Update all dates in LengthOfStay.csv by adding 12 years
Convert 2012 dates to 2024, etc.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def update_dates():
    """Update all dates by adding 12 years"""
    
    file_path = '/Users/pc/Documents/cursor/ml_course/project/data/LengthOfStay.csv'
    print("Loading CSV file...")
    df = pd.read_csv(file_path)
    
    print(f"Dataset shape: {df.shape}")
    
    # Find date columns by examining the data
    print("Examining columns for dates...")
    for col in df.columns:
        sample_values = df[col].head().astype(str).tolist()
        print(f"{col}: {sample_values}")
    
    # Identify date columns (birth_date, admit_date, discharge_date)
    date_columns = []
    
    # Check each column for date patterns
    for col in df.columns:
        sample = str(df[col].iloc[0])
        # Check if it looks like a date (MM/DD/YYYY or M/D/YYYY)
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', sample):
            date_columns.append(col)
            print(f"Found date column: {col}")
    
    print(f"Date columns identified: {date_columns}")
    
    # Update each date column
    for col in date_columns:
        print(f"\nUpdating {col}...")
        
        # Show some original values
        print(f"Original sample values: {df[col].head().tolist()}")
        
        # Convert to datetime, add 12 years, convert back to string
        df[col] = pd.to_datetime(df[col], format='%m/%d/%Y')
        df[col] = df[col] + pd.DateOffset(years=12)
        df[col] = df[col].dt.strftime('%m/%d/%Y')
        
        # Show updated values
        print(f"Updated sample values: {df[col].head().tolist()}")
    
    # Also update birth years to maintain age consistency
    # The birth dates should also be updated to keep ages the same
    
    print(f"\nSaving updated CSV file...")
    df.to_csv(file_path, index=False)
    print("Done!")
    
    # Verify the changes
    print(f"\nVerification - first 5 rows of date columns:")
    for col in date_columns:
        if col in df.columns:
            print(f"{col}: {df[col].head().tolist()}")

if __name__ == "__main__":
    update_dates()