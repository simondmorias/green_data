#!/usr/bin/env python3
"""
Run all tests and validations
"""

import sys
import os
import subprocess

def run_validation():
    """Run constraint validation"""
    print("Running constraint validation...")
    result = subprocess.run([sys.executable, 'tests/validate_constraints.py'], 
                          capture_output=False, text=True)
    return result.returncode == 0

def run_tests():
    """Run data tests"""
    print("\nRunning data tests...")
    result = subprocess.run([sys.executable, 'tests/test_rgm_data.py'], 
                          capture_output=False, text=True)
    return result.returncode == 0

def run_visualizations():
    """Generate visualizations"""
    print("\nGenerating visualizations...")
    
    # Ensure tmp directory exists
    os.makedirs('tmp', exist_ok=True)
    
    success = True
    
    try:
        print("Generating market share visualization...")
        result = subprocess.run([sys.executable, 'tests/visualize_market_share.py'], 
                              capture_output=False, text=True)
        if result.returncode != 0:
            print("Market share visualization failed")
            success = False
    except Exception as e:
        print(f"Market share visualization failed: {e}")
        success = False
    
    try:
        print("Generating trends visualization...")
        result = subprocess.run([sys.executable, 'tests/visualize_trends.py'], 
                              capture_output=False, text=True)
        if result.returncode != 0:
            print("Trends visualization failed")
            success = False
    except Exception as e:
        print(f"Trends visualization failed: {e}")
        success = False
    
    return success

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run RGM data tests and validations')
    parser.add_argument('--validate', action='store_true', help='Run constraint validation')
    parser.add_argument('--test', action='store_true', help='Run data tests')
    parser.add_argument('--visualize', action='store_true', help='Generate visualizations')
    parser.add_argument('--all', action='store_true', help='Run all tests and visualizations')
    
    args = parser.parse_args()
    
    all_success = True
    
    if args.all or (not any([args.validate, args.test, args.visualize])):
        if not run_validation():
            all_success = False
        if not run_tests():
            all_success = False
        if not run_visualizations():
            all_success = False
    else:
        if args.validate:
            if not run_validation():
                all_success = False
        if args.test:
            if not run_tests():
                all_success = False
        if args.visualize:
            if not run_visualizations():
                all_success = False
    
    if all_success:
        print("\n✓ All requested operations completed successfully!")
    else:
        print("\n⚠ Some operations failed. Check the output above for details.")
        sys.exit(1)