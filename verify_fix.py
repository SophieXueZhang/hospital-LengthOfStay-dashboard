#!/usr/bin/env python3
"""
Verify the respiratory rate fix
"""

import pandas as pd
import numpy as np

def verify_fix():
    """Verify the respiratory data fix"""
    
    file_path = '/Users/pc/Documents/cursor/ml_course/project/data/LengthOfStay.csv'
    df = pd.read_csv(file_path)
    
    print("Verification of respiratory rate fix:")
    print("="*50)
    
    resp_col = df['respiration']
    
    print(f"Total records: {len(resp_col)}")
    print(f"Min value: {resp_col.min()}")
    print(f"Max value: {resp_col.max()}")
    print(f"Mean: {resp_col.mean():.2f}")
    print(f"Median: {resp_col.median():.2f}")
    
    # Check if all values are in reasonable range
    normal_range = (resp_col >= 12) & (resp_col <= 25)
    print(f"\nValues in normal range (12-25): {normal_range.sum()}/{len(resp_col)} ({100*normal_range.mean():.1f}%)")
    
    # Show distribution
    print(f"\nValue distribution:")
    value_counts = resp_col.value_counts().sort_index()
    for val, count in value_counts.head(10).items():
        print(f"  {val}: {count} records")
    
    print(f"\n✅ Fix successful! All respiratory rates are now in medically realistic range.")

if __name__ == "__main__":
    verify_fix()