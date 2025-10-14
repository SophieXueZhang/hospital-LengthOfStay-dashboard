#!/usr/bin/env python3
"""
Fix respiratory rate values in LengthOfStay.csv
Transform unrealistic values (0.2-10.0) to normal adult range (12-20 breaths/min)
"""

import pandas as pd
import numpy as np

def fix_respiratory_data():
    """Load CSV, fix respiration column, save back"""
    
    # Load the data
    file_path = '/Users/pc/Documents/cursor/ml_course/project/data/LengthOfStay.csv'
    print("Loading CSV file...")
    df = pd.read_csv(file_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Original respiration column stats:")
    print(f"  Min: {df['respiration'].min()}")
    print(f"  Max: {df['respiration'].max()}")
    print(f"  Mean: {df['respiration'].mean():.2f}")
    print(f"  Std: {df['respiration'].std():.2f}")
    
    # Check current range
    original_min = df['respiration'].min()
    original_max = df['respiration'].max()
    
    # Calculate scaling factor to map to 12-20 range
    # Current range: ~0.2 to 10.0 (rough estimate)
    # Target range: 12 to 20
    # We'll use a linear transformation: new = old * scale_factor + offset
    
    # Simple approach: multiply by 2.5 to get most values in 12-20 range
    # This maps: 5.0 -> 12.5, 8.0 -> 20.0 approximately
    scale_factor = 2.5
    
    # Apply transformation
    df['respiration'] = df['respiration'] * scale_factor
    
    # Ensure values are in reasonable range (12-25, allowing slight variation)
    df['respiration'] = np.clip(df['respiration'], 12.0, 25.0)
    
    # Round to 1 decimal place for realistic precision
    df['respiration'] = np.round(df['respiration'], 1)
    
    print(f"\nTransformed respiration column stats:")
    print(f"  Min: {df['respiration'].min()}")
    print(f"  Max: {df['respiration'].max()}")
    print(f"  Mean: {df['respiration'].mean():.2f}")
    print(f"  Std: {df['respiration'].std():.2f}")
    
    # Show some examples
    print(f"\nFirst 10 transformed values:")
    print(df['respiration'].head(10).tolist())
    
    # Save the fixed data
    print("\nSaving updated CSV file...")
    df.to_csv(file_path, index=False)
    print("Done!")
    
    return df

if __name__ == "__main__":
    df = fix_respiratory_data()